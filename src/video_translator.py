import os
import traceback
from pydub import AudioSegment
from .asr_module import AudioTranscriber
from .translation_module import TextTranslator
from .timestamp_aligner import TimestampAligner
from .utils.result_logger import ResultLogger

class VideoScriptTranslator:
    def __init__(self, output_dir='./output'):
        """
        初始化视频脚本翻译器
        
        Args:
            output_dir (str): 输出目录
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化组件
        self.transcriber = AudioTranscriber()
        self.translator = TextTranslator()
        self.aligner = TimestampAligner()
        
        # 初始化日志记录器
        self.logger = ResultLogger(output_dir)
        self.output_dir = output_dir
    
    def translate_video_script(self, video_path, output_dir=None):
        """
        翻译视频脚本的主方法
        
        Args:
            video_path (str): 输入视频路径
            output_dir (str, optional): 输出目录，默认为初始化时的目录
        
        Returns:
            dict: 翻译结果
        """
        # 使用指定或默认输出目录
        output_dir = output_dir or self.output_dir
        
        try:
            # 提取音频
            audio_path = self._extract_audio(video_path, output_dir)
            self.logger.log_extraction_result(video_path, audio_path)
            
            # 音频转录
            try:
                transcription = self.transcriber.transcribe_audio(audio_path)
                self.logger.log_transcription_result(transcription)
            except Exception as e:
                self.logger.log_error('音频转录', e)
                # 详细的错误跟踪信息
                with open(os.path.join(output_dir, 'transcription_error_trace.txt'), 'w') as f:
                    f.write(traceback.format_exc())
                raise
            
            # 翻译文本片段
            try:
                translated_segments = self.translator.translate_segments(transcription['segments'])
                self.logger.log_translation_result(transcription['segments'], translated_segments)
            except Exception as e:
                self.logger.log_error('文本翻译', e)
                # 详细的错误跟踪信息
                with open(os.path.join(output_dir, 'translation_error_trace.txt'), 'w') as f:
                    f.write(traceback.format_exc())
                raise
            
            # 对齐时间戳
            try:
                aligned_segments = self.aligner.align_timestamps(
                    transcription['segments'], 
                    translated_segments
                )
                self.logger.log_alignment_result(aligned_segments)
            except Exception as e:
                self.logger.log_error('时间戳对齐', e)
                # 详细的错误跟踪信息
                with open(os.path.join(output_dir, 'alignment_error_trace.txt'), 'w') as f:
                    f.write(traceback.format_exc())
                raise
            
            # 生成字幕和其他信息
            result = {
                'video_path': video_path,
                'audio_path': audio_path,
                'original_text': transcription['text'],
                'translated_text': ' '.join([seg['text'] for seg in aligned_segments]),
                'segments': aligned_segments
            }
            
            # 保存详细结果
            with open(os.path.join(output_dir, 'final_translation_result.json'), 'w', encoding='utf-8') as f:
                import json
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        except Exception as e:
            self.logger.log_error('整体翻译过程', e)
            # 总体错误跟踪
            with open(os.path.join(output_dir, 'overall_error_trace.txt'), 'w') as f:
                f.write(traceback.format_exc())
            raise
    
    def _extract_audio(self, video_path, output_dir):
        """
        从视频中提取音频
        
        Args:
            video_path (str): 输入视频路径
            output_dir (str): 输出目录
        
        Returns:
            str: 音频文件路径
        """
        # 生成唯一的音频文件名
        import uuid
        audio_filename = f'extracted_audio_{uuid.uuid4().hex}.wav'
        audio_path = os.path.join(output_dir, audio_filename)
        
        # 使用 ffmpeg 提取音频（需要预先安装 ffmpeg）
        import subprocess
        
        try:
            # 使用 subprocess 替代 os.system，更安全和可控
            result = subprocess.run([
                'ffmpeg', 
                '-i', video_path, 
                '-vn',  # 不包含视频流
                '-acodec', 'pcm_s16le', 
                '-ar', '44100', 
                '-ac', '2', 
                audio_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"音频提取失败: {result.stderr}")
            
            return audio_path
        
        except Exception as e:
            self.logger.log_error('音频提取', e)
            # 详细的错误跟踪信息
            with open(os.path.join(output_dir, 'audio_extraction_error_trace.txt'), 'w') as f:
                f.write(traceback.format_exc())
            raise
