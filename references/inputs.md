# 输入与转录

## 有字幕或转录

`--transcript` 接收 UTF-8 编码的 VTT、SRT、TXT、MD 或 JSON。TXT / MD 保留原文，时间标记不自动解析；若要自动规划片段，建议使用字幕或规范 JSON：

```json
{"segments":[{"start":0,"end":6,"text":"第一段内容"}]}
```

JSON 时间可为秒数或 `HH:MM:SS.mmm`。脚本的 `supplied_transcript` 只表示用户提供了文件；若知道它由其他服务生成，在最终笔记补充真实来源，不改称本地 Whisper。

## 在线视频

```sh
python3 scripts/video_pack.py prepare --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --title "视频标题" --output ./runs/first-video
```

依赖 FFmpeg 和 yt-dlp。默认请求 `zh.*,en.*` 的平台字幕（包括自动字幕）；多个有效文件按文件名排序取第一个。需要固定语言时设置 `--sub-langs "zh-Hans"` 或 `"en"`，最终核对转录语言及字幕内容。无有效字幕则尝试本地 Whisper。

站点是否可下载取决于 yt-dlp、站点规则和用户的访问权限；遇到访问限制，保留日志，优先让用户提供本地视频和字幕。脚本禁用 yt-dlp 的本地配置加载，不自动读取浏览器登录状态。只有用户明确提供 cookies 文件时才加 `--cookies /path/to/cookies.txt`，使用临时副本并在退出时清除该副本；原文件保持不变。输出中的下载日志可能包含源链接，分享前按实际内容检查。

## 本地 Whisper（可选）

先按 [whisper.cpp 官方说明](https://github.com/ggml-org/whisper.cpp#quick-start) 安装 `whisper-cli`，准备兼容的 GGML 模型。项目不下载或捆绑模型。传入可执行文件与模型路径：

```sh
python3 scripts/video_pack.py prepare --video /path/to/video.mp4 \
  --whisper-bin /path/to/whisper-cli --whisper-model /path/to/ggml-small.bin \
  --language zh --title "视频标题" --output ./runs/local-asr
```

也支持 `WHISPER_CPP_BIN` 与 `WHISPER_MODEL` 环境变量。默认语言检测为 `auto`。语音先转换为 16 kHz 单声道 WAV，转写成功后移除中间 WAV，原始 JSON / VTT / TXT 和运行日志保存在 `asr/`。该分支没有说话人身份分离、云端章节或 PPT 抽取。字幕中的专名、数字和术语结合截图复核。

云端转录结果可以导出为支持的字幕格式，通过 `--transcript` 导入；此版本不内置云账号或云端上传适配器。
