from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import threading
import json
import os
import sys
from generate_html_with_data import generate_html_with_data

# 加载配置
def load_config():
    # 确定应用程序路径
    if getattr(sys, 'frozen', False):
        # 打包后的应用
        application_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    config_path = os.path.join(application_path, "config.json")
    
    # 如果配置文件存在，则加载
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                print(f"已从 {config_path} 加载配置")
                return config
        except Exception as e:
            error_msg = f"加载配置文件时出错: {e}"
            print(error_msg)
            messagebox.showerror("配置错误", error_msg)
            sys.exit(1)
    else:
        error_msg = f"找不到配置文件: {config_path}"
        print(error_msg)
        messagebox.showerror("配置错误", error_msg)
        sys.exit(1)

# 搜索热门视频
def search_hot_slots_videos(youtube, time_window_hours, search_query, max_results):
    # 计算time_window_hours小时前的时间
    now = datetime.now(timezone.utc)
    published_after = now - timedelta(hours=time_window_hours)
    # 转换为RFC 3339格式
    published_after_str = published_after.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    request = youtube.search().list(
        q=search_query,
        part="id,snippet",
        maxResults=max_results,
        order="viewCount",
        type="video",
        publishedAfter=published_after_str  # 只获取指定时间之后的视频
    )
    response = request.execute()
    return response

# 获取视频详细信息
def get_video_details(youtube, video_ids):
    request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    )
    response = request.execute()
    return response

# 主函数
def main(api_key, time_window_hours, search_query, max_results, output_file, status_callback=None):
    # 初始化YouTube API客户端
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # 更新状态
    if status_callback:
        status_callback("正在搜索热门视频...")
    
    # 搜索热门视频
    search_response = search_hot_slots_videos(youtube, time_window_hours, search_query, max_results)
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    
    # 更新状态
    if status_callback:
        status_callback("正在获取视频详细信息...")
    
    # 获取视频详细信息
    video_details = get_video_details(youtube, video_ids)
    
    # 更新状态
    if status_callback:
        status_callback("正在处理视频数据...")
    
    # 整理数据
    videos_info = []
    current_time = datetime.now(timezone.utc)
    
    for item in video_details['items']:
        # 解析发布时间 (格式如: '2023-04-25T12:00:00Z')
        published_at_str = item['snippet']['publishedAt']
        # 移除 'Z' 并添加 '+00:00' 表示 UTC
        if published_at_str.endswith('Z'):
            published_at_str = published_at_str[:-1] + '+00:00'
        published_at = datetime.fromisoformat(published_at_str)
        
        # 计算发布时间与当前时间的差值（小时）
        time_diff = current_time - published_at
        hours_diff = time_diff.total_seconds() / 3600
        
        # 只保留在时间窗口内且不晚于当前时间的视频
        if 0 <= hours_diff <= time_window_hours:
            video_info = {
                "title": item['snippet']['title'],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "published_at": published_at_str,
                "view_count": item['statistics']['viewCount']
            }
            videos_info.append(video_info)
    
    # 保存结果到文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(videos_info, f, ensure_ascii=False, indent=4)
    
    # 生成包含数据的HTML文件
    html_file = None
    try:
        html_file = generate_html_with_data(output_file, auto_open=True)
        if html_file and status_callback:
            status_callback(f"HTML文件 '{html_file}' 已成功生成并在浏览器中打开。")
    except Exception as e:
        if status_callback:
            status_callback(f"生成HTML文件时出错: {e}")
    
    # 更新状态
    if status_callback:
        status_callback(f"文件 '{output_file}' 已成功保存，共找到 {len(videos_info)} 个视频。")
    
    return output_file, len(videos_info), html_file

# 创建GUI应用
class SlotsVideoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # 定义百度风格的颜色主题
        self.colors = {
            "baidu_red": "#E02E2E",     # 百度红色
            "baidu_blue": "#4E6EF2",    # 百度蓝色
            "white": "#FFFFFF",         # 白色
            "light_gray": "#F5F5F6",    # 浅灰色
            "dark_gray": "#333333",     # 深灰色
            "border_gray": "#EAEAEA",   # 边框灰色
            "hover_blue": "#4662D9"     # 悬停蓝色
        }
        
        try:
            # 加载配置
            self.config = load_config()
            
            # 从配置中获取值
            self.default_api_key = self.config["API_KEY"]
            self.default_time_window_hours = self.config["DEFAULT_TIME_WINDOW_HOURS"]
            self.default_max_results = self.config["MAX_RESULTS"]
            self.default_search_query = self.config["SEARCH_QUERY"]
            
            # 确定输出文件路径（与config.json在同一路径）
            if getattr(sys, 'frozen', False):
                # 打包后的应用
                application_path = os.path.dirname(sys.executable)
            else:
                # 开发环境
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            self.output_file = os.path.join(application_path, "热门slots视频数据.json")
            
            # 设置窗口标题和大小
            self.title(self.config["APP_TITLE"])
            self.geometry(self.config["WINDOW_SIZE"])
            self.minsize(self.config["MIN_WINDOW_WIDTH"], self.config["MIN_WINDOW_HEIGHT"])
            
            # 设置窗口背景色
            self.configure(bg=self.colors["white"])
            
            # 创建自定义样式
            self.create_styles()
            
            # 创建UI
            self.create_ui()
        except Exception as e:
            messagebox.showerror("初始化错误", f"应用初始化失败: {e}")
            sys.exit(1)
    
    def create_styles(self):
        """创建自定义样式"""
        style = ttk.Style()
        
        # 配置整体主题
        style.theme_use('clam')  # 使用clam主题作为基础
        
        # 配置标签框架样式
        style.configure("TLabelframe", background=self.colors["white"], bordercolor=self.colors["border_gray"])
        style.configure("TLabelframe.Label", foreground=self.colors["dark_gray"], background=self.colors["white"], 
                        font=('Microsoft YaHei', 10))
        
        # 配置标签样式
        style.configure("TLabel", background=self.colors["white"], foreground=self.colors["dark_gray"], 
                        font=('Microsoft YaHei', 9))
        
        # 配置按钮样式 - 百度蓝色按钮
        style.configure("Baidu.TButton", background=self.colors["baidu_blue"], foreground=self.colors["white"], 
                        font=('Microsoft YaHei', 10), borderwidth=0, relief="flat")
        style.map("Baidu.TButton",
                  background=[('active', self.colors["hover_blue"]), ('pressed', self.colors["hover_blue"])],
                  foreground=[('active', self.colors["white"]), ('pressed', self.colors["white"])])
        
        # 配置进度条样式
        style.configure("TProgressbar", background=self.colors["baidu_blue"], troughcolor=self.colors["light_gray"], 
                        bordercolor=self.colors["border_gray"], lightcolor=self.colors["baidu_blue"], 
                        darkcolor=self.colors["baidu_blue"])
        
        # 配置输入框样式
        style.configure("TEntry", fieldbackground=self.colors["white"], bordercolor=self.colors["border_gray"])
        style.map("TEntry", 
                  fieldbackground=[('focus', self.colors["white"])],
                  bordercolor=[('focus', self.colors["baidu_blue"])])
        
        # 配置状态标签样式
        style.configure("Status.TLabel", foreground=self.colors["baidu_blue"], font=('Microsoft YaHei', 9))
        
        # 配置标题标签样式
        style.configure("Title.TLabel", foreground=self.colors["baidu_red"], background=self.colors["white"], 
                        font=('Microsoft YaHei', 14, 'bold'))
        
        # 配置结果标题样式
        style.configure("ResultTitle.TLabel", foreground=self.colors["dark_gray"], background=self.colors["white"], 
                        font=('Microsoft YaHei', 10))
        
        # 配置框架样式
        style.configure("TFrame", background=self.colors["white"])
    
    def create_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self, padding="20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 应用标题
        title_label = ttk.Label(main_frame, text="热门视频数据获取工具", style="Title.TLabel", anchor="center")
        title_label.pack(fill=tk.X, pady=(0, 20))
        
        # 配置信息设置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置信息", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 创建配置信息表格
        config_info = ttk.Frame(config_frame)
        config_info.pack(fill=tk.X, padx=5, pady=5)
        
        # 搜索关键词
        ttk.Label(config_info, text="搜索关键词:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.search_query_var = tk.StringVar(value=self.default_search_query)
        ttk.Entry(config_info, textvariable=self.search_query_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=8)
        
        # 最大结果数
        ttk.Label(config_info, text="最大结果数:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.max_results_var = tk.StringVar(value=str(self.default_max_results))
        ttk.Entry(config_info, textvariable=self.max_results_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=8)
        
        # 时间窗口设置
        ttk.Label(config_info, text="时间窗口（小时）:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=8)
        self.time_window_var = tk.StringVar(value=str(self.default_time_window_hours))
        ttk.Entry(config_info, textvariable=self.time_window_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=8)
        
        # API密钥
        ttk.Label(config_info, text="API密钥:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=8)
        self.api_key_var = tk.StringVar(value=self.default_api_key)
        ttk.Entry(config_info, textvariable=self.api_key_var, width=40).grid(row=3, column=1, sticky=tk.W, padx=5, pady=8)
        
        # 运行按钮 - 使用百度蓝色按钮样式
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.run_button = ttk.Button(button_frame, text="获取视频数据", command=self.run_search, style="Baidu.TButton")
        self.run_button.pack(fill=tk.X, pady=5)
        
        # 状态显示区域
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="状态:", style="ResultTitle.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
        status_label.pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(0, 20))
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="搜索结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 自定义结果文本区域样式
        self.result_text = scrolledtext.ScrolledText(
            result_frame, 
            height=15, 
            wrap=tk.WORD,
            font=('Microsoft YaHei', 9),
            background=self.colors["white"],
            foreground=self.colors["dark_gray"],
            borderwidth=1,
            relief="solid",
            padx=5,
            pady=5
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 设置应用图标（如果有）
        try:
            if getattr(sys, 'frozen', False):
                # 打包后的路径
                application_path = sys._MEIPASS
            else:
                # 开发环境路径
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass  # 忽略图标设置错误
    
    def update_status(self, message):
        """更新状态信息"""
        self.status_var.set(message)
        self.update_idletasks()
    
    def run_search(self):
        """运行搜索线程"""
        try:
            # 获取用户输入的值
            search_query = self.search_query_var.get().strip()
            if not search_query:
                messagebox.showerror("错误", "搜索关键词不能为空")
                return
                
            try:
                max_results = int(self.max_results_var.get())
                if max_results <= 0:
                    messagebox.showerror("错误", "最大结果数必须大于0")
                    return
            except ValueError:
                messagebox.showerror("错误", "请输入有效的最大结果数")
                return
                
            try:
                time_window = int(self.time_window_var.get())
                if time_window <= 0:
                    messagebox.showerror("错误", "时间窗口必须大于0")
                    return
            except ValueError:
                messagebox.showerror("错误", "请输入有效的时间窗口数值")
                return
            
            # 获取API密钥
            api_key = self.api_key_var.get().strip()
            if not api_key:
                messagebox.showerror("错误", "API密钥不能为空")
                return
            
            # 禁用按钮，启动进度条
            self.run_button.config(state=tk.DISABLED)
            self.progress.start()
            self.result_text.delete(1.0, tk.END)
            self.update_status("开始处理...")
            
            # 创建并启动工作线程
            thread = threading.Thread(target=self.search_thread, args=(api_key, search_query, max_results, time_window))
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("错误", f"启动搜索时出错: {e}")
    
    def search_thread(self, api_key, search_query, max_results, time_window):
        """后台搜索线程"""
        try:
            # 直接调用main函数，始终使用auto_open=True
            output_file, count, html_file = main(
                api_key, 
                time_window, 
                search_query, 
                max_results, 
                self.output_file, 
                self.update_status
            )
            
            # 读取并显示结果
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 在UI线程中更新结果
            self.after(0, lambda: self.show_results(data, output_file, html_file))
            
        except Exception as e:
            # 在UI线程中显示错误
            self.after(0, lambda: self.show_error(str(e)))
        finally:
            # 在UI线程中重置UI状态
            self.after(0, self.reset_ui)
    
    def show_results(self, data, output_file, html_file=None):
        """显示结果"""
        self.result_text.delete(1.0, tk.END)
        
        if not data:
            self.result_text.insert(tk.END, "未找到符合条件的视频")
            return
        
        # 设置标题样式
        title_font = font.Font(family="Microsoft YaHei", size=10, weight="bold")
        url_font = font.Font(family="Microsoft YaHei", size=9, underline=True)
        info_font = font.Font(family="Microsoft YaHei", size=9)
        
        for i, video in enumerate(data, 1):
            # 插入标题
            self.result_text.insert(tk.END, f"{i}. ", "index")
            self.result_text.insert(tk.END, f"{video['title']}\n", "title")
            
            # 插入链接
            self.result_text.insert(tk.END, f"   链接: ", "label")
            self.result_text.insert(tk.END, f"{video['url']}\n", "url")
            
            # 插入发布时间
            self.result_text.insert(tk.END, f"   发布时间: ", "label")
            self.result_text.insert(tk.END, f"{video['published_at']}\n", "info")
            
            # 插入观看次数
            self.result_text.insert(tk.END, f"   观看次数: ", "label")
            self.result_text.insert(tk.END, f"{video['view_count']}\n\n", "info")
        
        # 配置文本标签
        self.result_text.tag_configure("index", foreground=self.colors["baidu_red"], font=title_font)
        self.result_text.tag_configure("title", foreground=self.colors["dark_gray"], font=title_font)
        self.result_text.tag_configure("label", foreground=self.colors["baidu_blue"])
        self.result_text.tag_configure("url", foreground=self.colors["baidu_blue"], font=url_font)
        self.result_text.tag_configure("info", foreground=self.colors["dark_gray"], font=info_font)
    
    def show_error(self, error_message):
        """显示错误信息"""
        messagebox.showerror("错误", f"处理过程中出错:\n{error_message}")
        self.update_status(f"错误: {error_message}")
    
    def reset_ui(self):
        """重置UI状态"""
        self.run_button.config(state=tk.NORMAL)
        self.progress.stop()

if __name__ == "__main__":
    app = SlotsVideoApp()
    app.mainloop()
