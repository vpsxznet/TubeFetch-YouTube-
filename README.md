# TubeFetch

TubeFetch 是一个基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 的轻量级命令行工具，旨在帮助你快速解析并下载 YouTube 视频或音频。项目提供 Python API 与 CLI 两种使用方式，既适合直接在脚本中调用，也方便终端用户一键下载。

## 功能特性

- 🎬 提取视频基础信息（标题、作者、播放量等）
- 💾 下载视频或音频文件，默认选择最佳质量
- 🎛 支持自定义 `yt-dlp` 格式表达式与额外参数
- 🌐 支持代理配置，适应不同网络环境
- 🧰 提供高层封装 `VideoDownloader`，便于在 Python 项目中集成

## 环境准备

1. 安装 Python 3.10 及以上版本
2. 安装依赖：

   ```bash
   pip install -e .[dev]
   ```

   若只需运行 CLI，可省略 `.[dev]`，默认会安装核心依赖 `yt-dlp`。

## 命令行使用示例

```bash
# 下载视频到当前目录
python -m tube_fetch.cli "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 仅查看视频信息（JSON 格式）
python -m tube_fetch.cli "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --info --json

# 下载音频，并指定输出目录
python -m tube_fetch.cli "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --audio-only --output downloads/
```

更多参数可通过 `--help` 查看。

## Python API 使用示例

```python
from tube_fetch import VideoDownloader

video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

downloader = VideoDownloader()
info = downloader.fetch_info(video_url)
print(info.title)

path = downloader.download(video_url, audio_only=True)
print(f"Downloaded file stored at {path}")
```

## 运行测试

```bash
pytest
```

## 许可证

本项目采用 MIT 许可证发布。
