# 验证记录

## 本地验证

2026-11-09，在 macOS、Python 3.12 上完成：

- 19 项自动检查通过，覆盖时间解析、字幕格式、选段范围与预算、显式下载参数、安装不覆盖，以及 FFmpeg 实际抽帧、输出保留和失败清理。
- 原创演示完成视频＋字幕材料准备、三段抽帧；逐张打开 00:03、00:09、00:15 图片，依据实际内容写出示例笔记。
- yt-dlp 从本地 HTTP 服务下载本项目视频，配合字幕成功生成材料包；没有使用浏览器会话。
- 使用已有 whisper.cpp `whisper-cli` 与 `ggml-small.bin`，对本地合成的一段原创英文测试语音完成真实转写，识别出“First, read the transcript. Next, select the frames. Finally, write notes with timestamps.”，结果保存了真实引擎和模型来源。该测试音频未随项目发布。
- 主题封面、实际帧和示例笔记预览逐图检查；项目内链接及公开文件内容在发布前核对。

## CI

GitHub Actions 在 Linux / macOS、Python 3.10 运行相同测试与 CLI 检查，状态见仓库 [Actions](https://github.com/Jiale077/video-vision-summary/actions)。CI 不下载 Whisper 模型、不访问外部视频站点，也不运行大模型分析。

## 验证范围

没有在本次发布中实测各个 YouTube / Bilibili 链接、登录状态或全部字幕语言；下载能力由外部 yt-dlp 和站点访问条件决定。本地 HTTP 下载测试不能代表所有平台可用。Windows 未实测。

示例视频是无音轨的原创静态演示，用于证明材料准备与帧笔记链路。ASR 单独验证过，但不代表对其他录音、语言和领域专名的识别准确率。AI 分析通过本次宿主的实际看图和写作完成，最终质量随所用模型及输入变化。
