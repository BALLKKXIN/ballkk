import os

from PIL import Image
from moviepy import *


def generate_thumbnail(original_path, thumbnail_path):
    try:
        # 检查目标保存目录是否存在，如果不存在则创建
        thumbnail_dir = os.path.dirname(thumbnail_path)
        if not os.path.exists(thumbnail_dir):
            os.makedirs(thumbnail_dir)

        if original_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            img = Image.open(original_path)
            img.thumbnail((300, 300), Image.LANCZOS)
            img.save(thumbnail_path)
            return thumbnail_path
        #elif original_path.lower().endswith(('.mp4', '.mov', '.avi')):
            clip = VideoFileClip(original_path)
            frame = clip.get_frame(0)
            img = Image.fromarray(frame)
            img.thumbnail((100, 100), Image.LANCZOS)
            img.save(thumbnail_path)
            clip.close()
            return thumbnail_path
        return None
    except Exception as e:
        print(f"生成缩略图时出错: {e}")
        return None


def generate_compressed_video(original_path, compressed_path):
    try:
        # 检查目标保存目录是否存在，如果不存在则创建
        compressed_dir = os.path.dirname(compressed_path)
        if not os.path.exists(compressed_dir):
            os.makedirs(compressed_dir)

        clip = VideoFileClip(original_path)
        clip = clip.resized(height=240)  # 将 resize 改为 resized
        clip.write_videofile(compressed_path, codec='libx264')
        clip.close()
        return compressed_path
    except Exception as e:
        print(f"生成压缩视频时出错: {e}")
        return None


def get_mimetype(filename):
    if filename.lower().endswith(('.png')):
        return 'image/png'
    elif filename.lower().endswith(('.jpg', '.jpeg')):
        return 'image/jpeg'
    elif filename.lower().endswith(('.gif')):
        return 'image/gif'
    elif filename.lower().endswith(('.mp4')):
        return 'video/mp4'
    elif filename.lower().endswith(('.mov')):
        return 'video/quicktime'
    elif filename.lower().endswith(('.avi')):
        return 'video/x-msvideo'
    return 'application/octet-stream'


# 新增删除缩略图和压缩视频文件的函数
def delete_thumbnail_and_video(thumbnail_path, compressed_video_path):
    try:
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        if compressed_video_path and os.path.exists(compressed_video_path):
            os.remove(compressed_video_path)
    except Exception as e:
        print(f"删除缩略图或压缩视频文件时出错: {e}")