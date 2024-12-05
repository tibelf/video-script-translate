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
    
    def transcribe_audio(self, audio_path, segment_by_length=False, length=50):
        """
        转录音频文件
        
        Args:
            audio_path (str): 音频文件路径
            segment_by_length (bool): 是否根据固定文本长度进行切分
            length (int): 固定文本长度，默认为50
        
        Returns:
            dict: 包含文本和时间戳的字典
        """
        # Transcribe without punctuation argument
        result = self.model.transcribe(audio_path, word_timestamps=True)
        
        # 提取带时间戳的文本片段
        segments = []
        if segment_by_length:
            # Segment by fixed text length
            text = result['text']
            for i in range(0, len(text), length):
                segment_text = text[i:i+length].strip()
                segments.append({
                    'text': segment_text,
                    'start': None,  # Start time not applicable for fixed length
                    'end': None     # End time not applicable for fixed length
                })
        else:
            # Segment by natural speech segments
            for segment in result['segments']:
                segments.append({
                    'text': segment['text'].strip(),
                    'start': segment['start'],
                    'end': segment['end']
                })
        
        return {
            'text': result['text'],
            'segments': segments
        }
