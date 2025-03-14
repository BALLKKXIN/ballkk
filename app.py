from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from database import init_db, get_media_info, generate_all_media, delete_media_from_db, check_and_clean_media
import threading
import schedule
import time

from media_utils import *

# 定义外部缓存目录路径
#EXTERNAL_CACHE_DIR = os.path.abspath('../cache')  # 修改为你想要的外部目录路径

app = Flask(__name__)
CORS(app)
init_db()

# 启动时检查和清理
check_and_clean_media()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_media', methods=['GET'])
def get_media():
    try:
        media = get_media_info()
        return jsonify(media)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate_media', methods=['POST'])
def generate_media():
    def generate_media_in_thread():
        try:
            result = generate_all_media()
        except Exception as e:
            print(f"生成媒体文件时出错: {e}")

    threading.Thread(target=generate_media_in_thread).start()
    return jsonify({"message": "开始生成媒体文件"})


@app.route('/cache/<path:filename>')
def cache(filename):
    #return send_from_directory(EXTERNAL_CACHE_DIR, filename)
    # 使用绝对路径来查找文件
    return send_from_directory(EXTERNAL_CACHE_DIR, filename, as_attachment=False)


#media_dir = os.path.abspath('../media')
media_dir = EXTERNAL_MEDIA_DIR
@app.route('/<path:filename>')
def media(filename):
    # 使用绝对路径来查找文件
    return send_from_directory(EXTERNAL_MEDIA_DIR, filename, as_attachment=False)


@app.route('/delete_media/<path:original_path>', methods=['DELETE'])
def delete_media(original_path):
    print(f"接收到删除请求，原始路径: {original_path}")
    try:
        # 调用数据库中删除媒体记录的函数
        delete_media_from_db(original_path)
        # 删除原文件
        original_file_path = os.path.join('media', original_path)
        if os.path.exists(original_file_path):
            os.remove(original_file_path)
        return jsonify({"message": "媒体文件删除成功"})
    except Exception as e:
        print(f"删除媒体文件时出错: {e}")
        return jsonify({"error": str(e)}), 500


# 定义定期检查和清理的函数
def run_check_and_clean():
    check_and_clean_media()


# 每天凌晨 2 点执行检查和清理操作
schedule.every().day.at("02:00").do(run_check_and_clean)


if __name__ == '__main__':
    # 启动一个线程来运行定时任务
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)


    schedule_thread = threading.Thread(target=run_schedule)
    # TODO schedule_thread.start()

    # app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True)
