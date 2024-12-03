import warnings
import torch
import numpy as np

# 处理 NumPy 版本兼容性警告
warnings.filterwarnings('ignore', message='.*NumPy 1.x.*')

from transformers import AutoTokenizer, AutoModel

class TimestampAligner:
    def __init__(self):
        """
        初始化用于文本对齐的模型
        """
        # 明确指定 torch 的默认设备
        torch.set_default_device('cpu')
        
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
        # 确保模型在 CPU 上
        self.model.to('cpu')
    
    def compute_embedding(self, text):
        """
        计算文本的嵌入向量
        
        Args:
            text (str): 输入文本
        
        Returns:
            torch.Tensor: 文本的嵌入向量
        """
        try:
            # 使用更安全的 NumPy 操作
            tokens = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt")
            with torch.no_grad():
                model_output = self.model(**tokens)
            
            return model_output.last_hidden_state.mean(dim=1)
        except Exception as e:
            print(f"Embedding computation error: {e}")
            # 返回一个零向量作为备选
            return torch.zeros(1, 384)
    
    def align_timestamps(self, src_segments, translated_segments):
        """
        对齐原始文本和翻译文本的时间戳
        
        Args:
            src_segments (List[Dict]): 原始文本片段
            translated_segments (List[Dict]): 翻译文本片段
        
        Returns:
            List[Dict]: 对齐时间戳的翻译片段
        """
        aligned_segments = []
        
        for src_seg, trans_seg in zip(src_segments, translated_segments):
            try:
                src_emb = self.compute_embedding(src_seg['text'])
                trans_emb = self.compute_embedding(trans_seg['text'])
                
                # 使用余弦相似度评估文本相似度
                similarity = torch.nn.functional.cosine_similarity(src_emb, trans_emb)
                
                if similarity > 0.7:  # 相似度阈值
                    aligned_segments.append({
                        'text': trans_seg['text'],
                        'start': src_seg['start'],
                        'end': src_seg['end']
                    })
                else:
                    aligned_segments.append(trans_seg)
            except Exception as e:
                print(f"Timestamp alignment error: {e}")
                aligned_segments.append(trans_seg)
        
        return aligned_segments
