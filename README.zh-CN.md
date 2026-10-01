[English](README.md)

# PhyCo Gravity Dataset

我们使用 PhyCo-Sim 场景生成的四档重力视频数据，共 **1,000 段 RGB 视频、250 个基础场景、8 种场景类型**。这是本项目生成的数据集；上游模拟管线为 [PhyCo-Sim](https://github.com/nnsriram97/phyco-sim)，固定版本为 `bd8a3b4eb54fa1ad008250e2033a1f8369bff6d3`。

完整数据位于本仓库的 **[Releases / v1.0.0](https://github.com/primorLee/phyco-gravity-1000/releases/tag/v1.0.0)**，分成 5 个文件，总计 **4,756,459,520 字节（约 4.43 GiB）**。仓库中的 JSONL 清单可直接用于读取数据。

## 数据规模

| 项目 | 内容 |
|---|---|
| 重力 | 0.1g、0.3g、0.5g、1g，各 250 段；1g = 9.8 m/s² |
| 基础场景 | 250 组，每组对应四档重力 |
| 训练集 | 800 段、200 个基础场景 |
| 独立测试集 | 200 段、50 个基础场景 |
| 划分方式 | 按整个基础场景划分；训练集和测试集的基础场景重叠为 0 |
| 原始视频 | 768 × 432，24 fps；752 段为 98 帧，248 段为 97 帧 |
| 输出 | RGB 视频、首帧、逐帧图像、分割/深度输出、物理状态和模拟参数 |
| 全部文件 | 207,008 个；其中 3,000 个 MP4 包括 RGB 及辅助视频，并非 3,000 个独立样本 |

### 场景类型

| 类型 | 标识 | 基础场景数 | RGB 视频数 |
|---|---|---:|---:|
| 单球下落 | `ball_drop_v2` | 32 | 128 |
| 多球下落 | `ball_drop_v3` | 32 | 128 |
| 平面滑动 | `friction_slide_flat` | 31 | 124 |
| 软球下落 | `ball_drop_soft_v4` | 31 | 124 |
| 软立方体形变 | `cube_deform_soft_v2` | 31 | 124 |
| 外力推动滑动 | `friction_slide_flat_force` | 31 | 124 |
| 积木塔外力 | `jenga_force` | 31 | 124 |
| 台球外力 | `pool_table_force` | 31 | 124 |

“基础场景”表示一组场景配置和随机种子。对同一基础场景分别设置四档重力，得到四段视频。提示词同时写明运动描述和重力数值。

## 下载与解压

数据无需登录即可从公开 Release 下载。也可安装 GitHub CLI，然后在本仓库目录中运行：

```bash
gh release download v1.0.0 --repo primorLee/phyco-gravity-1000 --pattern "phyco-gravity-1000.tar.part*" --dir parts
python extract_dataset.py --parts parts --output data
```

`extract_dataset.py` 只使用 Python 标准库（Python 3.10+）。它先校验每个分包和完整归档的 SHA-256，再直接流式解压；不额外生成一份合并后的大 TAR。请使用空的输出目录，磁盘至少预留约 10 GiB（分包和解压后的数据共同占用空间）。

分包校验和在 `SHA256SUMS`，机器可读的文件大小、顺序和校验和在 `distribution.json`。

## 读取样本

`manifests/all.jsonl`、`manifests/train.jsonl`、`manifests/heldout.jsonl` 分别包含 1,000、800、200 条记录。`video`、`first_frame`、`sample_directory` 均相对于解压目录 `data/`。

```python
import json
from pathlib import Path

dataset_root = Path("data")
with Path("manifests/train.jsonl").open(encoding="utf-8") as f:
    sample = json.loads(next(f))

video = dataset_root / sample["video"]
first_frame = dataset_root / sample["first_frame"]
prompt = sample["prompt"]
gravity = sample["gravity_scale"]
```

每个样本目录还保留 `physics.json`、`physics_states.npz`、`visibility.json`、原始元数据和完成记录。归档保留了原始文件，其中部分原始清单使用生成机器的绝对路径；跨机器使用时应优先采用本仓库 `manifests/` 下的相对路径清单。

## 生成来源与已知边界

沿用上述 PhyCo-Sim 版本的场景及参数采样，修改模拟器重力，添加重力提示词、配对种子、首帧与物理状态导出。素材来自本项目已缓存的 Poly Haven 材质和 HDRI 子集；本数据不是作者完整素材库的逐文件复刻。

- 原始视频保持生成时的真实帧数和 24 fps，不包含训练时另行制作的 33 帧或 97 帧裁剪缓存。
- 官方渲染流程可能在物体静止后复用图像帧，相关信息保留在逐样本元数据中。
- 相同随机种子不保证全部场景的四档首帧像素完全相同：`jenga_force_0010` 已观察到首帧构型差异。需要严格相同初态的实验应逐组筛选。
- 文件完整性、视频解码检查和训练/测试划分已完成；这些检查不等同于每段画面和物理轨迹均已人工验收。

原始数据包 SHA-256：

```text
b91b2f5b8bf6e4a983b65ac229eec006b42a060d10f21e2874bf62b1b42fb8d6
```

## 许可与引用

数据与清单按 **CC BY-NC 4.0** 发布，要求署名且仅限非商业使用；解压工具按 MIT 发布。
请引用本数据集，并保留对 PhyCo-Sim 和 PhyCo 论文作者的致谢。详见 [英文 README](README.md#license-and-citation)、[数据许可](LICENSE)、[代码许可](LICENSE-CODE.txt) 和 [上游来源](THIRD_PARTY_NOTICES.md)。
