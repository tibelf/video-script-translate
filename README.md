# Video Script Translate 项目

## 项目介绍
这是一个基于 Python 的视频脚本翻译工具，可以：
- 从视频中提取音频
- 进行语音识别（ASR）
- 翻译文本
- 保持原始时间戳对齐

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用示例
```python
from src.video_translator import VideoScriptTranslator

translator = VideoScriptTranslator()
result = translator.translate_video_script(
    'input_video.mp4', 
    'output_directory'
)
print(result['translated_text'])
```

## 依赖库
- Whisper (语音识别)
- Google Translate
- PyTorch
- Transformers
