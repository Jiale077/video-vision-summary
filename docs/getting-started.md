# 使用教程

## 1. 准备运行环境

安装 Python 3.10+ 和 FFmpeg，确认 `python3 --version`、`ffmpeg -version` 能运行。

macOS 使用 Homebrew 时：

```sh
brew install python ffmpeg
```

Ubuntu / Debian：

```sh
sudo apt-get update
sudo apt-get install python3 ffmpeg
```

其他平台按 [FFmpeg 官网](https://ffmpeg.org/download.html) 安装并放入 PATH。脚本使用跨平台 Python 与 FFmpeg 命令；当前自动验证覆盖 Linux / macOS，Windows 未做实际运行验证，可能需把 `python3` 改成 `python`。

仅在线下载分支需要 yt-dlp。建议放入单独环境：

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U yt-dlp
```

YouTube 等站点的额外依赖按 [yt-dlp 官方说明](https://github.com/yt-dlp/yt-dlp#dependencies) 安装。使用站点字幕时仍需下载视频供抽帧。

运行 `python3 scripts/video_pack.py doctor`。已有字幕路线只需 `ffmpeg: true`；另外两项是可选能力。

## 2. 安装与第一次使用

在仓库根目录，按 [README 的安装命令](../README.md#安装技能) 复制技能，然后按 [第一个例子](../README.md#跑通第一个例子) 生成材料包。安装器不会覆盖已有同名目录。

脚本运行位置与分析输出位置可以不同；路径中有空格时使用引号。助手执行命令时应先定位安装技能的实际脚本路径，不依赖作者机器的目录。

## 3. 换成你自己的视频

### 本地视频＋字幕

```sh
python3 scripts/video_pack.py prepare \
  --video "/path/to/course.mp4" --transcript "/path/to/course.srt" \
  --title "课程标题" --output runs/course-01
```

支持 VTT / SRT、纯文本与 Markdown，以及 [规范 JSON](../references/inputs.md#有字幕或转录)。文本稿缺少结构化时间轴时，脚本保留全文，AI 应先取得时间轴或实际播放定位，不能凭内容编造时间。

### 在线链接

```sh
python3 scripts/video_pack.py prepare \
  --url "https://www.bilibili.com/video/BV_REPLACE_ME" \
  --sub-langs "zh.*" --title "视频标题" --output runs/online-01
```

将占位链接替换为实际视频。默认一次处理一个视频，不展开播放列表。平台字幕优先；没有可用字幕时，需配置本地 Whisper。已有本地字幕也可同时加 `--transcript`。

若站点明确要求登录，可自行提供 Netscape 格式 cookies 文件并加 `--cookies /path/to/cookies.txt`。该动作由你明确选择；脚本仅使用临时副本，原文件不改动。不要把 cookies 与私人视频提交到仓库。下载的 source/、日志和转录都位于你选择的输出目录。

### 没有字幕：本地 Whisper

按 [输入与转录](../references/inputs.md#本地-whisper可选) 准备 whisper.cpp 和模型，然后：

```sh
python3 scripts/video_pack.py prepare \
  --video "/path/to/course.mp4" \
  --whisper-bin "/path/to/whisper-cli" \
  --whisper-model "/path/to/ggml-small.bin" \
  --language zh --title "课程标题" --output runs/asr-01
```

转写需要视频中有音轨。仓库 demo 是无音轨测试视频，请用自己的带语音视频体验 ASR。模型精度取决于模型、录音与语言，数字和专有名词结合画面核对。

## 4. 怎么选关键片段

准备完成后，让 AI 阅读 `plan.prompt.md` 和 `transcript.md`，保存 `segments.json`：

```json
{
  "key_segments": [
    {"start":"00:02:10","end":"00:02:30","reason":"核对架构图中的模块和箭头","expected_visuals":"系统架构图"},
    {"start":"00:05:00","end":"00:05:20","reason":"补全代码中的参数名","expected_visuals":"代码编辑器"}
  ]
}
```

使用真实时间轴。优先挑“只听讲解还不够理解”的位置；口播视频可用 `{"key_segments":[]}`。默认每段取 3 张，均匀采在段内，总计最多 12 张。超过预算会明确报错，可缩短或减少选段、降低 `--per-segment`，或显式提高 `--max-frames`（最多 100）。

```sh
python3 scripts/video_pack.py frames \
  --pack runs/course-01 --segments runs/course-01/segments.json \
  --per-segment 3 --max-frames 12 --width 1280
```

图片按采样时间排列。`expected_visuals` 是预期，实际看过之后才知道有没有这些内容。此版使用确定的时间采样，保留时间与文件的一一对应，没有自动场景检测。

## 5. 写成能复用的笔记

让助手按 `analyze.prompt.md` **实际打开所有待引用图片**，结合转录，参考 [笔记模板](../references/note-template.md) 写到材料包中的 `note.md`。至少核对三点：

1. 每个画面判断都有具体截图与时间，模糊文字标注待核实。
2. 字幕原意、画面所见和分析推断分别表达，有冲突保留双方。
3. 图片采用相对路径，整个材料包移动后仍可阅读。

如果继续使用原本地视频抽帧，`manifest.json` 中的相对 media 路径必须仍能找到原视频。在线下载的视频放在材料包 source/。分享笔记可以只带转录、笔记和引用图片；私人内容先自行确认分享范围。

## 常见问题

| 现象 | 处理方式 |
| --- | --- |
| 找不到 FFmpeg | 安装后确认 `ffmpeg -version` 可运行，重开终端或助手会话 |
| 没有字幕，也没有 whisper-cli / 模型 | 先提供字幕，或配置 `--whisper-bin`、`--whisper-model` |
| 输出目录已经存在 | 选择新的输出目录；已有分析与笔记保留 |
| 提示本材料包已有帧 | 当前实现每包抽帧一次；如要调整，创建新材料包再抽帧 |
| 时间超出视频或结束时间早于开始 | 检查选段范围，使用 `HH:MM:SS.mmm` 或秒数 |
| 平台 403、登录限制、字幕下载失败 | 查看 download.log；更新 yt-dlp，或提供本地视频与字幕 |
| 帧里正好是过场或内容不完整 | 缩短选段，增加采样点，或实际播放复核 |
| 图片已提取，但 AI 说无法读取 | 使用支持图片查看的宿主；当前只能交付文字分析 |

[返回项目首页](../README.md)
