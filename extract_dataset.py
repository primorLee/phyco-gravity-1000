# SPDX-License-Identifier: MIT
"""Verify the release parts, then extract without writing a merged TAR."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile


class PartReader(io.RawIOBase):
    def __init__(self, files):
        self.files = iter(files)
        self.current = None

    def readable(self): return True

    def read(self, size=-1):
        if size < 0: raise ValueError('Unbounded reads are disabled')
        result = bytearray()
        while len(result) < size:
            if self.current is None:
                file = next(self.files, None)
                if file is None: break
                self.current = file.open('rb')
            data = self.current.read(size - len(result))
            if data: result.extend(data)
            else:
                self.current.close(); self.current = None
        return bytes(result)

    def close(self):
        if self.current: self.current.close()
        super().close()


def verify(parts, spec):
    full = hashlib.sha256(); files = []
    for record in spec['parts']:
        path = parts / record['name']
        if not path.is_file() or path.stat().st_size != record['bytes']:
            raise ValueError('Missing or incomplete part: ' + path.name)
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(4 * 1024**2), b''):
                digest.update(block); full.update(block)
        if digest.hexdigest() != record['sha256']:
            raise ValueError('Checksum mismatch: ' + path.name)
        files.append(path); print('Verified', path.name, flush=True)
    if full.hexdigest() != spec['archive_sha256']:
        raise ValueError('Combined archive checksum mismatch')
    return files


def extract(files, output, expected_files):
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a new or empty output directory; existing data is never overwritten')
    output.mkdir(parents=True, exist_ok=True)
    count = 0
    with PartReader(files) as reader, tarfile.open(fileobj=reader, mode='r|') as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts:
                raise ValueError('Unsafe archive path')
            target = (output / Path(*name.parts)).resolve()
            if not target.is_relative_to(output): raise ValueError('Archive path escapes output')
            if member.isdir(): target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, target.open('xb') as destination:
                    shutil.copyfileobj(source, destination, length=1024**2)
                if target.stat().st_size != member.size: raise ValueError('Incomplete extraction')
                count += 1
                if count % 10000 == 0: print('Extracted', count, 'files', flush=True)
            else: raise ValueError('Unexpected archive member type')
    if count != expected_files: raise ValueError(f'Expected {expected_files} files, extracted {count}')
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parts', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(Path(__file__).with_name('distribution.json').read_text())
    files = verify(args.parts, spec)
    count = extract(files, args.output, spec['source_file_count'])
    print(f'Complete: {count} files in {args.output.resolve()}')


if __name__ == '__main__': main()
