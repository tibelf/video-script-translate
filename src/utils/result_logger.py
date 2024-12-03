import os
import json
import logging
from datetime import datetime

class ResultLogger:
    def __init__(self, output_dir):
        """
        初始化结果记录器
        
        Args:
            output_dir (str): 输出目录
        """
        self.output_dir = output_dir
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 配置日志记录器
        log_path = os.path.join(output_dir, 'video_translation.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_extraction_result(self, video_path, audio_path):
        """
        记录音频提取结果
        """
        self.logger.info(f"音频提取完成: {video_path} -> {audio_path}")
        
        # 保存提取信息
        extraction_info = {
            'video_path': video_path,
            'audio_path': audio_path,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(os.path.join(self.output_dir, 'audio_extraction.json'), 'w', encoding='utf-8') as f:
            json.dump(extraction_info, f, ensure_ascii=False, indent=2)
    
    def log_transcription_result(self, transcription_result):
        """
        记录语音转录结果
        """
        self.logger.info(f"语音转录完成，总文本长度：{len(transcription_result['text'])}")
        
        # 保存转录详细信息
        with open(os.path.join(self.output_dir, 'transcription_segments.json'), 'w', encoding='utf-8') as f:
            json.dump(transcription_result, f, ensure_ascii=False, indent=2)
    
    def log_translation_result(self, transcription_segments, translated_segments):
        """
        记录翻译结果
        """
        self.logger.info(f"翻译完成，原始段落数：{len(transcription_segments)}，翻译段落数：{len(translated_segments)}")
        
        # 保存原始和翻译的详细对比
        translation_comparison = []
        for src, trans in zip(transcription_segments, translated_segments):
            translation_comparison.append({
                'source_text': src['text'],
                'source_start': src['start'],
                'source_end': src['end'],
                'translated_text': trans['text']
            })
        
        with open(os.path.join(self.output_dir, 'translation_comparison.json'), 'w', encoding='utf-8') as f:
            json.dump(translation_comparison, f, ensure_ascii=False, indent=2)
    
    def log_alignment_result(self, aligned_segments):
        """
        记录时间戳对齐结果
        """
        self.logger.info(f"时间戳对齐完成，总段落数：{len(aligned_segments)}")
        
        with open(os.path.join(self.output_dir, 'aligned_segments.json'), 'w', encoding='utf-8') as f:
            json.dump(aligned_segments, f, ensure_ascii=False, indent=2)
    
    def log_error(self, stage, error):
        """
        记录错误信息
        """
        self.logger.error(f"错误发生在 {stage} 阶段: {str(error)}")
        
        error_info = {
            'stage': stage,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(os.path.join(self.output_dir, 'error_log.json'), 'w', encoding='utf-8') as f:
            json.dump(error_info, f, ensure_ascii=False, indent=2)
