# batch_headless.py 使用说明 / User Guide

## 功能 | Features
- 批量处理 input_dir 目录下所有视频文件。
  Batch process all video files in the input_dir directory.
- 每个视频先用 ffmpeg 分割为 5 份。
  Each video is split into 5 parts using ffmpeg.
- 每一份用 facefusion headless-run 处理，输出到临时目录。
  Each part is processed by facefusion headless-run and output to a temp directory.
- 处理完的 5 份再用 ffmpeg 合并为一个完整输出视频，输出到 output_dir。
  The 5 processed parts are merged into a complete output video using ffmpeg, saved to output_dir.
- 自动清理所有临时分段文件。
  All temporary segment files are automatically cleaned up.

## 用法 | Usage
```bash
python batch_headless.py
```

## 依赖 | Dependencies
- 需要已安装 ffmpeg/ffprobe（命令行可用）
  ffmpeg/ffprobe must be installed and available in your shell.
- 需要 facefusion 环境可用
  facefusion environment must be available.
- 请确保 temp_dir 有足够磁盘空间（建议 1T 以上）
  Make sure temp_dir has enough disk space (suggested 1TB+).

## 注意事项 | Notes
- source_img 可指定为单张参考图片，如需批量换脸可自行扩展。
  source_img can be set to a single reference image; for batch face swap, extend as needed.
- 脚本默认分 5 段，如需更改可修改 split_video 函数的 parts 参数。
  The script splits into 5 parts by default; change the parts parameter in split_video if needed.
- 合并时采用无损拼接，部分格式可能需转码。
  Merging uses lossless concat; some formats may require transcoding.
- 运行前请确保 input_dir、output_dir、temp_dir 路径存在且有写权限。
  Ensure input_dir, output_dir, and temp_dir exist and are writable before running.
