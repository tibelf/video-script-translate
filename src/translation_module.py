from deep_translator import GoogleTranslator
from typing import List, Dict
import time
import random

class TextTranslator:
    def __init__(self, max_retries=3):
        """
        初始化翻译器
        
        Args:
            max_retries (int): 最大重试次数
        """
        self.translator = GoogleTranslator()
        self.max_retries = max_retries
    
    def translate_segments(self, segments: List[Dict], src_lang='zh-cn', dest_lang='en'):
        """
        翻译文本片段，带重试机制
        
        Args:
            segments (List[Dict]): 原始文本片段
            src_lang (str): 源语言
            dest_lang (str): 目标语言
        
        Returns:
            List[Dict]: 翻译后的文本片段
        """
        translated_segments = []
        
        for segment in segments:
            for attempt in range(self.max_retries):
                try:
                    translated_text = self.translator.translate(
                        segment['text'], 
                        source=src_lang, 
                        target=dest_lang
                    )
                    
                    translated_segments.append({
                        'text': translated_text,
                        'start': segment['start'],
                        'end': segment['end']
                    })
                    break
                
                except Exception as e:
                    print(f"Translation attempt {attempt + 1} failed: {e}")
                    
                    # 指数退避策略
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) + random.random()
                        print(f"Waiting {wait_time:.2f} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        print(f"Failed to translate segment: {segment['text']}")
                        # 如果翻译失败，保留原文
                        translated_segments.append(segment)
        
        return translated_segments
