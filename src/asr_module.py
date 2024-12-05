import whisper
import torch
import numpy as np
from pydub import AudioSegment
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification,BertTokenizerFast,AutoModel

class AudioTranscriber:
    def __init__(self, model_size='base'):
        """
        初始化音频转录模型
        
        Args:
            model_size (str): Whisper模型大小，默认为 'base'
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = whisper.load_model(model_size, device=self.device)
        
    def add_punctuation(self, text):
        """
        使用 BERT 分类器为文本添加标点符号
        
        Args:
            text (str): 需要添加标点的文本
        
        Returns:
            str: 添加标点后的文本
        """
        try:
            # 加载专门用于中文的模型
            tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
            model = AutoModel.from_pretrained('bert-base-chinese')
            model = model.to(self.device)
            
            # 对文本进行分词
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            inputs = inputs.to(self.device)
            
            # 获取模型预测
            with torch.no_grad():
                outputs = model(**inputs)
                # 使用最后一层的隐藏状态
                hidden_states = outputs.last_hidden_state
                
                # 使用隐藏状态的均值作为特征
                features = torch.mean(hidden_states, dim=2)
            
            # 将预测结果转换为标点符号
            tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            punctuated_text = ""
            last_token = ""
            
            for i, token in enumerate(tokens):
                # 跳过特殊标记
                if token in ['[CLS]', '[SEP]', '[PAD]']:
                    continue
                    
                # 移除 ## 开头的 token（BERT分词的特殊标记）
                if token.startswith("##"):
                    token = token[2:]
                    
                punctuated_text += token
                
                # 根据上下文添加标点符号
                if i > 0 and i < len(tokens) - 2:  # 避免在开头和结尾处添加标点
                    # 在语气词后添加标点
                    if token in ['的', '了', '吗', '呢', '啊', '吧']:
                        if '吗' in token:
                            punctuated_text += '？'
                        else:
                            punctuated_text += '，'
                    # 在句子较长时添加句号
                    elif i % 10 == 0 and len(punctuated_text) > 20:
                        if not punctuated_text.endswith(('。', '，', '！', '？')):
                            punctuated_text += '。'
                    # 在特定词后添加逗号
                    elif token in ['是', '有', '会'] and not punctuated_text.endswith(('。', '，', '！', '？')):
                        punctuated_text += '，'
                
                last_token = token
            
            # 确保文本以句号结尾
            if not punctuated_text.endswith(('。', '！', '？')):
                punctuated_text += '。'
                
            return punctuated_text
            
        except Exception as e:
            print(f"添加标点符号时发生错误: {str(e)}")
            return text

    def needs_punctuation(self, text):
        """检查文本末尾是否需要添加标点符号"""
        # 如果文本已经以标点符号结尾，则返回 False
        if text and text[-1] in ['。', '，', '！', '？', '；', '：']:
            return False
        return True
        
    def merge_texts(self, text1, text2):
        """合并两段文本，处理标点符号"""
        text1 = text1.strip()
        text2 = text2.strip()
            
        # 如果第一段文本需要标点符号
        print(f"text1: {text1}")
        if self.needs_punctuation(text1):
            # 根据语境判断使用逗号还是句号
            # 如果第二段文本很短或者明显是同一句话的延续，使用逗号
            if len(text2) < 10 or text2.startswith(('而且', '并且', '但是', '因为')):
                text1 += '，'
            else:
                text1 += '。'
            
        # 确保两段文本之间有适当的空格或标点
        return f"{text1}{text2}"
    
    def merge_short_segments(self, segments, min_duration=3.0, max_duration=30.0):
        """
        合并过短的片段，分割过长的片段，同时处理段落间的标点符号
        
        Args:
            segments (list): 原始片段列表
            min_duration (float): 最小片段时长（秒）
            max_duration (float): 最大片段时长（秒）
        """
        merged = []
        current = None
        
        
        for segment in segments:
            if not current:
                current = segment.copy()
                continue
                
            duration = segment['end'] - segment['start']
            current_duration = current['end'] - current['start']
            
            # 如果当前片段太短，且与下一个片段合并后不会太长，则合并
            if current_duration < min_duration and (current_duration + duration) <= max_duration:
                # 合并文本时处理标点符号
                current['text'] = self.merge_texts(current['text'], segment['text'])
                current['end'] = segment['end']
            else:
                # 在添加到 merged 列表前确保当前片段有合适的结束标点
                if self.needs_punctuation(current['text']):
                    current['text'] += '。'
                merged.append(current)
                current = segment.copy()
        
        # 处理最后一个片段
        if current:
            if self.needs_punctuation(current['text']):
                current['text'] += '。'
            merged.append(current)
        
        return merged

    def transcribe_audio(self, audio_path, segment_by_length=False, length=50, 
                        min_segment_duration=3.0, max_segment_duration=30.0):
        """
        转录音频文件
        
        Args:
            audio_path (str): 音频文件路径
            segment_by_length (bool): 是否根据固定文本长度进行切分
            length (int): 固定文本长度，默认为50
            min_segment_duration (float): 最小片段时长（秒）
            max_segment_duration (float): 最大片段时长（秒）
        """
        result = self.model.transcribe(audio_path, word_timestamps=True)

        # Add punctuation to the transcribed text
        punctuated_text = self.add_punctuation(result['text'])
        
        print("\n--- 添加标点后的文本 ---")
        print(punctuated_text)
        
        segments = []
        if segment_by_length:
            # 按固定长度分段的逻辑保持不变
            #text = result['text']
            for i in range(0, len(punctuated_text), length):
                segment_text = punctuated_text[i:i+length].strip()
                segments.append({
                    'text': segment_text,
                    'start': None,
                    'end': None
                })
        else:
            # 使用自定义分段逻辑
            original_segments = [
                {
                    'text': segment['text'].strip(),
                    'start': segment['start'],
                    'end': segment['end']
                }
                for segment in result['segments']
            ]
            
            # 应用自定义分段规则
            segments = self.merge_short_segments(
                original_segments,
                min_duration=min_segment_duration,
                max_duration=max_segment_duration
            )
        
        return {
            'text': punctuated_text,
            'segments': segments
        }
