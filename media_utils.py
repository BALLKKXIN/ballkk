import os

from PIL import Image
from moviepy import VideoFileClip
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')
MEDIA_DIR = config.get('media','media_dir')
CACHE_DIR = config.get('media', 'cache_dir')
THUMBNAIL_WIDTH = int(config.get('media', 'thumbnail_width'))
THUMBNAIL_HEIGHT = int(config.get('media', 'thumbnail_height'))
THUMBNAIL_VIDEO_HEIGHT = int(config.get('media', 'thumbnail_video_height'))

EXTERNAL_CACHE_DIR = os.path.abspath(CACHE_DIR)  # 修改为你想要的外部目录路径
EXTERNAL_MEDIA_DIR = os.path.abspath(MEDIA_DIR)  # 修改为你想要的外部目录路径

# 定义外部缓存目录路径
#EXTERNAL_CACHE_DIR = os.path.abspath('../cache')  # 修改为你想要的外部目录路径

def generate_thumbnail(original_path, thumbnail_path):
    try:
        # 检查目标保存目录是否存在，如果不存在则创建
        thumbnail_dir = os.path.dirname(thumbnail_path)
        if not os.path.exists(thumbnail_dir):
            os.makedirs(thumbnail_dir)

        if original_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            img = Image.open(original_path)
            img.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), Image.LANCZOS)
            img.save(thumbnail_path)
            print(f"完成G{thumbnail_path}")
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
        clip_duration = clip.duration
        if clip_duration > 5:
            clip = clip.subclipped(0, 5)
        clip = clip.resized(height=THUMBNAIL_VIDEO_HEIGHT)
        clip.write_videofile(compressed_path, codec='libx264')
        clip.close()
        print(f"完成V{compressed_path}")
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