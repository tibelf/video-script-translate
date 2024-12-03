import os
import sys
import argparse
import json
import traceback
from datetime import datetime
from src.video_translator import VideoScriptTranslator

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='视频脚本翻译工具')
    parser.add_argument('input_video', help='输入视频文件路径')
    parser.add_argument('--output_dir', 
                        default=None, 
                        help='输出目录，默认为 ./output/[当前日期时间]')
    parser.add_argument('--src_lang', 
                        default='zh-cn', 
                        help='源语言，默认为中文')
    parser.add_argument('--dest_lang', 
                        default='en', 
                        help='目标语言，默认为英文')
    parser.add_argument('--debug', 
                        action='store_true', 
                        help='启用详细调试信息')
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果未指定输出目录，则生成基于当前时间的目录
    if not args.output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = os.path.join('./output', f'translation_{timestamp}')
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 初始化翻译器
    try:
        translator = VideoScriptTranslator(output_dir=args.output_dir)
        
        # 执行翻译
        result = translator.translate_video_script(
            args.input_video, 
            args.output_dir
        )
        
        # 如果是调试模式，打印更多详细信息
        if args.debug:
            print("\n--- 详细翻译结果 ---")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 输出基本结果
        print("\n--- 原始文本 ---")
        print(result['original_text'])
        
        print("\n--- 翻译文本 ---")
        print(result['translated_text'])
        
        # 保存翻译结果到文本文件（人类可读）
        output_text_file = os.path.join(args.output_dir, 'translation_result.txt')
        with open(output_text_file, 'w', encoding='utf-8') as f:
            f.write("原始文件: " + args.input_video + "\n\n")
            f.write("原始文本:\n")
            f.write(result['original_text'] + "\n\n")
            f.write("翻译文本:\n")
            f.write(result['translated_text'])
        
        # 导出详细的分段信息
        segments_file = os.path.join(args.output_dir, 'translation_segments.txt')
        with open(segments_file, 'w', encoding='utf-8') as f:
            f.write("时间戳\t原始文本\t翻译文本\n")
            for segment in result['segments']:
                f.write(f"{segment['start']:.2f} - {segment['end']:.2f}\t{segment['text']}\n")
        
        print(f"\n翻译结果已保存到目录: {args.output_dir}")
        print(f"文本翻译结果: {output_text_file}")
        print(f"分段信息: {segments_file}")
    
    except Exception as e:
        print(f"翻译过程出错: {e}")
        
        # 在错误目录保存详细错误信息
        error_log_file = os.path.join(args.output_dir, 'translation_error.log')
        with open(error_log_file, 'w', encoding='utf-8') as f:
            f.write(f"错误信息: {str(e)}\n\n")
            f.write("详细错误追踪:\n")
            f.write(traceback.format_exc())
        
        print(f"详细错误日志已保存到: {error_log_file}")
        sys.exit(1)

if __name__ == '__main__':
    main()
