const generateButton = document.getElementById('generate-button');
const progressInfoDiv = document.getElementById('progress-info');
const mediaGroupsDiv = document.getElementById('media-groups');
const fullscreenOverlay = document.getElementById('fullscreen-overlay');
const fullscreenContent = document.getElementById('fullscreen-content');
const leftArrow = document.getElementById('left-arrow');
const rightArrow = document.getElementById('right-arrow');
let observer;
let isGenerating = false;
let currentIndex = 0;

if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                if (el.tagName === 'IMG') {
                    const thumbnailPath = el.dataset.thumbnail;
                    // 修改路径处理逻辑
                    el.src = `/cache/${thumbnailPath.replace('cache\\', '')}`;
                } else if (el.tagName === 'VIDEO') {
                    const compressedVideoPath = el.dataset.compressed;
                    // 修改路径处理逻辑
                    el.src = `/cache/${compressedVideoPath.replace('cache\\', '')}`;
                }
                observer.unobserve(el);
            }
        });
    }, {
        rootMargin: '0px',
        threshold: 0.1
    });
}

function checkAndLoadMedia() {
    const mediaElements = document.querySelectorAll('.media-container img, .media-container video');
    mediaElements.forEach(el => {
        const path = el.tagName === 'IMG'? el.dataset.thumbnail : el.dataset.compressed;
        // 修改路径处理逻辑
        const url = `/cache/${path.replace('cache\\', '')}`;
        const xhr = new XMLHttpRequest();
        xhr.open('HEAD', url, false);
        xhr.send();
        if (xhr.status === 200) {
            if (el.tagName === 'IMG') {
                el.src = url;
            } else if (el.tagName === 'VIDEO') {
                el.src = url;
            }
        } else {
            if (observer) {
                observer.observe(el);
            }
        }
    });
}

generateButton.addEventListener('click', () => {
    if (isGenerating) {
        return;
    }
    isGenerating = true;
    generateButton.disabled = true;
    progressInfoDiv.innerHTML = "正在生成媒体缩略图和压缩视频，请稍候...";
    fetch('/generate_media', {
        method: 'POST'
    })
      .then(response => response.json())
      .then(data => {
            if (data.message === "开始生成媒体文件") {
                setTimeout(() => {
                    fetch('/get_media')
                      .then(response => {
                            if (!response.ok) {
                                throw new Error(`网络请求失败，状态码：${response.status}`);
                            }
                            return response.json();
                        })
                      .then(media => {
                            mediaGroupsDiv.innerHTML = '';
                            for (const date in media) {
                                const dateGroupDiv = document.createElement('div');
                                dateGroupDiv.classList.add('date-group');

                                const dateHeader = document.createElement('h2');
                                dateHeader.textContent = date;
                                dateGroupDiv.appendChild(dateHeader);

                                const mediaContainer = document.createElement('div');
                                mediaContainer.classList.add('media-container');

                                const mediaList = media[date];
                                mediaList.forEach(item => {
                                    if (item.is_video) {
                                        const video = document.createElement('video');
                                        video.dataset.compressed = item.compressed_video_path;
                                        video.dataset.original = item.original_path;
                                        video.muted = true;
                                        video.loop = true;
                                        video.addEventListener('mouseenter', () => {
                                            video.play();
                                        });
                                        video.addEventListener('mouseleave', () => {
                                            video.pause();
                                        });
                                        video.addEventListener('click', () => {
                                            // 使用外部路径
                                            const originalUrl = item.original_path; 
                                            fullscreenContent.innerHTML = `<video id="fullscreen-media" controls src="${originalUrl}"></video>`;
                                            fullscreenOverlay.style.display = 'flex';
                                        });
                                        mediaContainer.appendChild(video);
                                        if (observer) {
                                            observer.observe(video);
                                        }
                                    } else {
                                        const img = document.createElement('img');
                                        img.dataset.thumbnail = item.thumbnail_path;
                                        img.dataset.original = item.original_path;
                                        img.addEventListener('click', () => {
                                            const allImages = document.querySelectorAll('.media-container img');
                                            const imgPaths = Array.from(allImages).map(img => img.dataset.original);
                                            currentIndex = imgPaths.indexOf(item.original_path);
                                            // 使用外部路径
                                            const originalUrl = item.original_path; 
                                            showFullscreenImage(originalUrl);
                                        });
                                        mediaContainer.appendChild(img);
                                        if (observer) {
                                            observer.observe(img);
                                        }
                                    }
                                });

                                dateGroupDiv.appendChild(mediaContainer);
                                mediaGroupsDiv.appendChild(dateGroupDiv);
                            }
                            checkAndLoadMedia();
                            isGenerating = false;
                            generateButton.disabled = false;
                            progressInfoDiv.innerHTML = `总共 ${data.total} 个媒体文件，已处理 ${data.generated} 个`;
                        })
                      .catch(error => {
                            console.error('获取媒体信息时出错:', error);
                            isGenerating = false;
                            generateButton.disabled = false;
                        });
                }, 5000);
            } else {
                progressInfoDiv.innerHTML = "媒体文件处理失败";
                console.error('媒体文件处理失败');
                isGenerating = false;
                generateButton.disabled = false;
            }
        })
      .catch(error => {
            progressInfoDiv.innerHTML = "生成媒体文件请求出错";
            console.error('生成媒体文件请求出错:', error);
            isGenerating = false;
            generateButton.disabled = false;
        });
});

// 页面加载时获取媒体信息并展示
fetch('/get_media')
  .then(response => {
        if (!response.ok) {
            throw new Error(`网络请求失败，状态码：${response.status}`);
        }
        return response.json();
    })
  .then(media => {
        for (const date in media) {
            const dateGroupDiv = document.createElement('div');
            dateGroupDiv.classList.add('date-group');

            const dateHeader = document.createElement('h2');
            dateHeader.textContent = date;
            dateGroupDiv.appendChild(dateHeader);

            const mediaContainer = document.createElement('div');
            mediaContainer.classList.add('media-container');

            const mediaList = media[date];
            mediaList.forEach(item => {
                if (item.is_video) {
                    const video = document.createElement('video');
                    video.dataset.compressed = item.compressed_video_path;
                    video.dataset.original = item.original_path;
                    console.log('视频原始路径:', item.original_path); // 调试信息，查看路径是否正确
                    video.muted = true;
                    video.loop = true;
                    video.addEventListener('mouseenter', () => {
                        video.play();
                    });
                    video.addEventListener('mouseleave', () => {
                        video.pause();
                    });
                    video.addEventListener('click', () => {
                        // 使用外部路径
                        const originalUrl = item.original_path; 
                        console.log('点击视频请求的 URL:', originalUrl); // 调试信息，查看构建的 URL
                        fullscreenContent.innerHTML = `<video id="fullscreen-media" controls src="${originalUrl}"></video>`;
                        fullscreenOverlay.style.display = 'flex';
                    });
                    // 初始不设置 src 属性
                    video.controls = false; 
                    mediaContainer.appendChild(video);
                    if (observer) {
                        observer.observe(video);
                    }
                } else {
                    const img = document.createElement('img');
                    img.dataset.thumbnail = item.thumbnail_path;
                    img.dataset.original = item.original_path;
                    console.log('图片原始路径:', item.original_path); // 调试信息，查看路径是否正确
                    img.addEventListener('click', () => {
                        const allImages = document.querySelectorAll('.media-container img');
                        const imgPaths = Array.from(allImages).map(img => img.dataset.original);
                        currentIndex = imgPaths.indexOf(item.original_path);
                        // 使用外部路径
                        const originalUrl = item.original_path; 
                        console.log('点击图片请求的 URL:', originalUrl); // 调试信息，查看构建的 URL
                        showFullscreenImage(originalUrl);
                    });
                    // 初始不设置 src 属性
                    img.src = ''; 
                    mediaContainer.appendChild(img);
                    if (observer) {
                        observer.observe(img);
                    }
                }
            });

            dateGroupDiv.appendChild(mediaContainer);
            mediaGroupsDiv.appendChild(dateGroupDiv);
        }
        // 移除不必要的预加载检查
        // checkAndLoadMedia(); 
        generateButton.disabled = false;
    })
  .catch(error => {
        console.error('获取媒体信息时出错:', error);
        generateButton.disabled = false;
    });

// 关闭全屏查看
fullscreenOverlay.addEventListener('click', (event) => {
    // 检查点击的是否是全屏覆盖层本身或全屏内容区域以外的元素
    if (event.target === fullscreenOverlay || event.target === fullscreenContent) {
        fullscreenOverlay.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

// 点击缩略图时显示全屏内容并禁用滚动条
const mediaElements = document.querySelectorAll('.media-container img, .media-container video');
mediaElements.forEach(el => {
    el.addEventListener('click', () => {
        document.body.style.overflow = 'hidden';
    });
});

// 显示全屏图片的函数
function showFullscreenImage(url) {
    // 这里假设 url 已经是外部路径
    fullscreenContent.innerHTML = `<img id="fullscreen-media" src="${url}">`;
    fullscreenOverlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// 左箭头点击事件处理
leftArrow.addEventListener('click', (event) => {
    const allImages = document.querySelectorAll('.media-container img');
    const imgPaths = Array.from(allImages).map(img => img.dataset.original);
    if (currentIndex > 0) {
        currentIndex--;
        showFullscreenImage(imgPaths[currentIndex]);
    }
    // 阻止事件冒泡，避免触发全屏覆盖层的点击事件
    event.stopPropagation(); 
});

// 右箭头点击事件处理
rightArrow.addEventListener('click', (event) => {
    const allImages = document.querySelectorAll('.media-container img');
    const imgPaths = Array.from(allImages).map(img => img.dataset.original);
    if (currentIndex < imgPaths.length - 1) {
        currentIndex++;
        showFullscreenImage(imgPaths[currentIndex]);
    }
    // 阻止事件冒泡，避免触发全屏覆盖层的点击事件
    event.stopPropagation(); 
});