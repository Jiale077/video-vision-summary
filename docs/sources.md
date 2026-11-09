# 资料与依赖

核对日期：2026-11-09。项目的公开实现为独立编写；未复制旧安装中的浏览器 cookies、私人输出或第三方分析提示词包。

| 一手来源 | 本项目参考的内容 |
| --- | --- |
| [Codex 技能说明](https://learn.chatgpt.com/docs/build-skills) | SKILL.md 及个人 `.agents/skills` 安装位置 |
| [Claude Code 技能说明](https://code.claude.com/docs/en/skills) | 个人 `.claude/skills` 安装位置与刷新方式 |
| [yt-dlp 官方仓库](https://github.com/yt-dlp/yt-dlp#usage-and-options) | 在线下载、字幕、显式 cookies 和 `--ignore-config` |
| [whisper.cpp 官方仓库](https://github.com/ggml-org/whisper.cpp#quick-start) | 本地可执行文件、模型与转录；本机还核对了实际 CLI 参数 |
| [FFmpeg 官方文档源码](https://github.com/FFmpeg/FFmpeg/blob/master/doc/ffmpeg.texi) | 输入、时间定位与帧输出；具体抽帧命令经过媒体测试 |

这些工具单独安装，不随本项目分发。它们的许可证和模型使用条件以各自项目为准。

封面采用“Jiale的AI工坊”的暖白、墨线、橙色重点和少量青绿色结果标记；为 AI 生成的主题插画，提示词见 [cover-prompt.md](cover-prompt.md)。示例的 3 张 SVG 幻灯片、对应 PNG 和字幕为本项目原创。PNG 由浏览器按 960×540 渲染 SVG，MP4 可用 `python3 examples/build_demo.py --output /path/to/new-demo.mp4` 从 PNG 重建。
