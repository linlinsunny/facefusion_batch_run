
"""
批量分段处理 FaceFusion 脚本
--------------------------
功能：
    1. 遍历 input_dir 目录下所有视频文件。
    2. 每个视频用 ffmpeg 分割为 5 份。
    3. 每一份用 facefusion headless-run 处理，输出到临时目录。
    4. 处理完的 5 份再用 ffmpeg 合并为一个完整输出视频，输出到 output_dir。
    5. 自动清理所有临时分段文件。

用法：
    python batch_headless.py

依赖：
    - 需要已安装 ffmpeg/ffprobe（命令行可用）
    - 需要 facefusion 环境可用
    - 请确保 temp_dir 有足够磁盘空间（建议 1T 以上）

注意事项：
    - source_img 可指定为单张参考图片，如需批量换脸可自行扩展。
    - 脚本默认分 5 段，如需更改可修改 split_video 函数的 parts 参数。
    - 合并时采用无损拼接，部分格式可能需转码。
"""
import os
import subprocess

# 配置路径
source_img = "/Volumes/JBOD/Ff/ref/1.jpeg"  # 可修改为你要用的参考图片
input_dir = "/Volumes/JBOD/Ff/input"		# 需要处理的视频文件目录
output_dir = "/Volumes/JBOD/Ff/output"		# 处理完的输出目录
temp_dir = "/Volumes/JBOD/Ff/temp_batch"	# 临时文件目录请保证有 1T 以上的空间
os.makedirs(temp_dir, exist_ok=True)

# 支持的视频扩展名
video_exts = (".mp4", ".mov", ".avi", ".mkv")

def get_video_duration(video_path):
    # 获取视频时长（秒）
    import json
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(result.stdout)
    return float(info['format']['duration'])

def split_video(input_path, temp_dir, parts=5):
    duration = get_video_duration(input_path)
    part_duration = duration / parts
    part_files = []
    for i in range(parts):
        start = i * part_duration
        part_file = os.path.join(temp_dir, f"part_{i}.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", input_path, "-ss", str(start), "-t", str(part_duration), "-c", "copy", part_file
        ]
        subprocess.run(cmd, check=True)
        part_files.append(part_file)
    return part_files

def process_parts(part_files, source_img, temp_dir):
    processed_files = []
    for i, part_file in enumerate(part_files):
        processed_file = os.path.join(temp_dir, f"processed_{i}.mp4")
        cmd = [
            "python", "facefusion.py", "headless-run",
            "--source-paths", source_img,
            "--target-path", part_file,
            "--output-path", processed_file
        ]
        print("处理分段:", " ".join(cmd))
        subprocess.run(cmd, check=True)
        processed_files.append(processed_file)
    return processed_files

def merge_videos(processed_files, output_path):
    # 生成合并列表文件
    list_file = os.path.join(os.path.dirname(output_path), "merge_list.txt")
    with open(list_file, "w") as f:
        for file in processed_files:
            f.write(f"file '{file}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_path
    ]
    subprocess.run(cmd, check=True)
    os.remove(list_file)

for filename in os.listdir(input_dir):
    if filename.lower().endswith(video_exts):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        print(f"\n处理视频: {input_path}")
        # 1. 分割视频
        part_files = split_video(input_path, temp_dir, parts=5)
        # 2. 处理每一段
        processed_files = process_parts(part_files, source_img, temp_dir)
        # 3. 合并处理后的视频
        merge_videos(processed_files, output_path)
        # 4. 清理临时分段
        for f in part_files + processed_files:
            if os.path.exists(f):
                os.remove(f)
