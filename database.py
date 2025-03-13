import sqlite3
import os
from datetime import datetime
from media_utils import delete_thumbnail_and_video

def init_db():
    conn = sqlite3.connect('media_cache.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS media_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_path TEXT UNIQUE,
            thumbnail_path TEXT,
            compressed_video_path TEXT,
            last_modified TIMESTAMP,
            is_video BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def get_media_info():
    conn = sqlite3.connect('media_cache.db')
    c = conn.cursor()
    c.execute('SELECT * FROM media_cache')
    rows = c.fetchall()
    media = {}
    for row in rows:
        _, original_path, thumbnail_path, compressed_video_path, last_modified, is_video = row
        try:
            # 去除 media 文件夹
            if original_path.startswith('media'):
                original_path = original_path.replace('media' + os.sep, '', 1)
            date = datetime.fromtimestamp(os.path.getmtime(os.path.join('media', original_path))).strftime('%Y-%m-%d')
            if date not in media:
                media[date] = []
            media[date].append({
                'original_path': original_path,
                'thumbnail_path': thumbnail_path,
                'compressed_video_path': compressed_video_path,
                'last_modified': last_modified,
                'is_video': is_video
            })
        except Exception as e:
            print(f"处理记录时出错: {e}, 原始路径: {original_path}")
    conn.close()
    return media

def generate_all_media():
    media_dir ='../media'
    conn = sqlite3.connect('media_cache.db')
    c = conn.cursor()
    total = 0
    generated = 0
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            total += 1
            file_path = os.path.join(root, file)
            c.execute('SELECT * FROM media_cache WHERE original_path =?', (file_path,))
            existing = c.fetchone()
            if existing:
                continue
            from media_utils import generate_thumbnail, generate_compressed_video, get_mimetype
            mimetype = get_mimetype(file)
            is_video = mimetype.startswith('video')
            # 构建缓存目录结构与实际相册目录一致
            relative_path = os.path.relpath(file_path, media_dir)
            cache_sub_dir = os.path.join('cache', os.path.dirname(relative_path))
            thumbnail_path = generate_thumbnail(file_path, os.path.join(cache_sub_dir, f'thumbnail_{os.path.basename(file_path)}'))
            compressed_video_path = None
            if is_video:
                compressed_video_path = generate_compressed_video(file_path, os.path.join(cache_sub_dir, f'compressed_{os.path.basename(file_path)}'))
            last_modified = datetime.now()
            try:
                c.execute('''
                    INSERT INTO media_cache (original_path, thumbnail_path, compressed_video_path, last_modified, is_video)
                    VALUES (?,?,?,?,?)
                ''', (file_path, thumbnail_path, compressed_video_path, last_modified, is_video))
                conn.commit()
                generated += 1
            except sqlite3.IntegrityError:
                conn.rollback()
    conn.close()
    return {
        "message": "媒体文件处理成功",
        "total": total,
        "generated": generated
    }

def delete_media_from_db(original_path):
    conn = sqlite3.connect('media_cache.db')
    c = conn.cursor()
    # 查询该原图对应的缩略图和压缩视频路径
    c.execute('SELECT thumbnail_path, compressed_video_path FROM media_cache WHERE original_path =?', (original_path,))
    result = c.fetchone()
    if result:
        thumbnail_path, compressed_video_path = result
        print(f"找到对应记录，缩略图路径: {thumbnail_path}，压缩视频路径: {compressed_video_path}")
        # 调用 media_utils 中的函数删除缩略图和压缩视频文件
        delete_thumbnail_and_video(thumbnail_path, compressed_video_path)
        # 从数据库中删除该记录
        c.execute('DELETE FROM media_cache WHERE original_path =?', (original_path,))
        conn.commit()
        print("数据库记录已删除")
    else:
        print("未找到对应记录")
    conn.close()

# 新增检查和清理函数
def check_and_clean_media():
    conn = sqlite3.connect('media_cache.db')
    c = conn.cursor()
    c.execute('SELECT original_path, thumbnail_path, compressed_video_path FROM media_cache')
    rows = c.fetchall()
    for original_path, thumbnail_path, compressed_video_path in rows:
        if not os.path.exists(original_path):
            try:
                # 删除缩略图和压缩视频文件
                delete_thumbnail_and_video(thumbnail_path, compressed_video_path)
                # 从数据库中删除记录
                c.execute('DELETE FROM media_cache WHERE original_path =?', (original_path,))
                conn.commit()
                print(f"已清理记录：{original_path}")
            except Exception as e:
                print(f"清理记录 {original_path} 时出错: {e}")
    conn.close()