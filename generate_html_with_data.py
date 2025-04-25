import json
import os
import sys
import webbrowser
from datetime import datetime

def generate_html_with_data(json_file_path, output_html_path=None, auto_open=True):
    """
    生成一个包含JSON数据的HTML文件，用于直接显示热门视频数据
    
    参数:
        json_file_path: JSON数据文件路径
        output_html_path: 输出HTML文件路径，如果为None，则使用默认路径
    
    返回:
        生成的HTML文件路径
    """
    # 确定输出HTML文件路径
    if output_html_path is None:
        # 使用与JSON文件相同的目录，但文件名为"视频数据.html"
        json_dir = os.path.dirname(os.path.abspath(json_file_path))
        output_html_path = os.path.join(json_dir, "视频数据.html")
    
    # 读取JSON数据
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件时出错: {e}")
        return None
    
    # 将JSON数据转换为JavaScript变量
    json_str = json.dumps(json_data, ensure_ascii=False)
    
    # HTML模板
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热门视频数据</title>
    <!-- 添加文件图标 -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🎰</text></svg>">
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        h1 {{
            color: #d32f2f;
            text-align: center;
            margin-bottom: 30px;
        }}
        .video-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        .video-card {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .video-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .video-thumbnail {{
            position: relative;
            width: 100%;
            padding-top: 56.25%; /* 16:9 比例 */
            background-color: #eee;
            overflow: hidden;
        }}
        .video-thumbnail img {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .video-thumbnail .play-button {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60px;
            height: 60px;
            background-color: rgba(255, 0, 0, 0.8);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .video-thumbnail .play-button:after {{
            content: '';
            display: block;
            width: 0;
            height: 0;
            border-top: 10px solid transparent;
            border-left: 20px solid white;
            border-bottom: 10px solid transparent;
            margin-left: 5px;
        }}
        .video-info {{
            padding: 15px;
        }}
        .video-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            line-height: 1.4;
            height: 44px;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }}
        .video-meta {{
            display: flex;
            justify-content: space-between;
            color: #666;
            font-size: 14px;
        }}
        .video-views {{
            display: flex;
            align-items: center;
        }}
        .video-views:before {{
            content: '👁️';
            margin-right: 5px;
        }}
        .video-date {{
            display: flex;
            align-items: center;
        }}
        .video-date:before {{
            content: '📅';
            margin-right: 5px;
        }}
        .loading {{
            text-align: center;
            padding: 50px;
            font-size: 18px;
            color: #666;
        }}
        .error {{
            text-align: center;
            padding: 20px;
            color: #d32f2f;
            background-color: #ffebee;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .data-source {{
            text-align: center;
            margin-top: 10px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>热门视频数据</h1>
    
    <div class="data-source" id="dataSource">数据来源: {os.path.basename(json_file_path)} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    
    <div id="error" class="error" style="display: none;"></div>
    <div id="loading" class="loading">正在加载数据...</div>
    <div id="videoContainer" class="video-container"></div>

    <script>
        // 内嵌的JSON数据
        const videoData = {json_str};
        
        // 格式化数字为带千位分隔符的形式
        function formatNumber(num) {{
            return new Intl.NumberFormat('zh-CN').format(num);
        }}

        // 格式化日期时间
        function formatDate(dateString) {{
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN', {{
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            }});
        }}

        // 从YouTube URL获取视频ID
        function getYoutubeVideoId(url) {{
            const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{{11}})/;
            const match = url.match(regex);
            return match ? match[1] : null;
        }}
        
        // 显示数据
        function displayData() {{
            const videoContainer = document.getElementById('videoContainer');
            const loadingElement = document.getElementById('loading');
            const errorElement = document.getElementById('error');
            
            // 隐藏加载中提示
            loadingElement.style.display = 'none';
            
            // 如果没有数据
            if (!videoData || videoData.length === 0) {{
                errorElement.textContent = '没有找到视频数据';
                errorElement.style.display = 'block';
                return;
            }}
            
            // 清空容器
            videoContainer.innerHTML = '';
            
            // 遍历数据并创建视频卡片
            videoData.forEach(video => {{
                const videoId = getYoutubeVideoId(video.url);
                const thumbnailUrl = videoId ? 
                    `https://img.youtube.com/vi/${{videoId}}/mqdefault.jpg` : 
                    'placeholder.jpg';
                
                const videoCard = document.createElement('div');
                videoCard.className = 'video-card';
                
                videoCard.innerHTML = `
                    <a href="${{video.url}}" target="_blank" rel="noopener noreferrer">
                        <div class="video-thumbnail">
                            <img src="${{thumbnailUrl}}" alt="${{video.title}}" loading="lazy">
                            <div class="play-button"></div>
                        </div>
                    </a>
                    <div class="video-info">
                        <div class="video-title">${{video.title}}</div>
                        <div class="video-meta">
                            <div class="video-views">${{formatNumber(video.view_count)}}</div>
                            <div class="video-date">${{formatDate(video.published_at)}}</div>
                        </div>
                    </div>
                `;
                
                videoContainer.appendChild(videoCard);
            }});
        }}

        // 页面加载完成后显示数据
        document.addEventListener('DOMContentLoaded', displayData);
    </script>
</body>
</html>
"""
    
    # 写入HTML文件
    try:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"已成功生成HTML文件: {output_html_path}")
        
        # 自动打开HTML文件
        if auto_open:
            try:
                webbrowser.open('file://' + os.path.abspath(output_html_path))
                print(f"已在默认浏览器中打开HTML文件")
            except Exception as e:
                print(f"打开浏览器时出错: {e}")
        
        return output_html_path
    except Exception as e:
        print(f"生成HTML文件时出错: {e}")
        return None

if __name__ == "__main__":
    # 如果作为独立脚本运行，获取命令行参数
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
        output_html_path = sys.argv[2] if len(sys.argv) > 2 else None
        auto_open = True
        if len(sys.argv) > 3:
            auto_open = sys.argv[3].lower() not in ('false', 'no', '0', 'n', 'f')
        generate_html_with_data(json_file_path, output_html_path, auto_open)
    else:
        # 默认使用当前目录下的"热门视频数据.json"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, "热门视频数据.json")
        if os.path.exists(json_file_path):
            generate_html_with_data(json_file_path)
        else:
            print(f"错误: 找不到文件 {json_file_path}")
            print("用法: python generate_html_with_data.py [JSON文件路径] [输出HTML路径(可选)]")
