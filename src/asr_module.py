import whisper
import torch
import numpy as np
from pydub import AudioSegment

class AudioTranscriber:
    def __init__(self, model_size='base'):
        """
        初始化音频转录模型
        
        Args:
            model_size (str): Whisper模型大小，默认为 'base'
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = whisper.load_model(model_size, device=self.device)
    
    def transcribe_audio(self, audio_path):
        """
        转录音频文件
        
        Args:
            audio_path (str): 音频文件路径
        
        Returns:
            dict: 包含文本和时间戳的字典
        """
        result = self.model.transcribe(audio_path, word_timestamps=True)
        
        # 提取带时间戳的文本片段
        segments = []
        for segment in result['segments']:
            for word in segment['words']:
                segments.append({
                    'text': word['word'].strip(),
                    'start': word['start'],
                    'end': word['end']
                })
        
        return {
            'text': result['text'],
            'segments': segments
        }
