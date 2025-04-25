# 热门视频获取工具

## 项目介绍

这是一个用于获取YouTube上热门视频数据的工具。该工具使用YouTube Data API获取指定时间窗口内的热门相关视频，并将数据保存为JSON格式，同时生成一个可视化的HTML页面用于查看数据。

## 主要功能

1. **获取热门视频数据**：根据指定的时间窗口获取YouTube上热门的相关视频
2. **数据可视化**：自动生成HTML页面，以卡片形式展示视频数据
3. **自动打开浏览器**：可选择是否在生成HTML文件后自动用默认浏览器打开
4. **灵活配置**：通过配置文件设置API密钥、搜索关键词等参数

## 文件说明

- `获取热门视频数据.py`：主程序文件
- `generate_html_with_data.py`：HTML生成模块
- `config.json`：配置文件
- `热门视频数据.json`：生成的数据文件
- `视频数据.html`：生成的HTML可视化页面
- `README.md`：本说明文件

## 使用方法

### 1. 配置文件

首先确保`config.json`文件包含正确的配置：

```json
{
  "API_KEY": "你的YouTube API密钥",
  "DEFAULT_TIME_WINDOW_HOURS": 24,
  "MAX_RESULTS": 10,
  "SEARCH_QUERY": "slots",
  "APP_TITLE": "热门视频获取工具",
  "WINDOW_SIZE": "600x500",
  "MIN_WINDOW_WIDTH": 500,
  "MIN_WINDOW_HEIGHT": 400
}
```

### 2. 运行程序

直接运行主程序：

```
python 获取热门视频数据.py
```

### 3. 使用界面

1. 设置时间窗口（小时）：指定要获取多少小时内发布的视频
2. 选择是否自动打开HTML文件：勾选后将在生成HTML文件后自动用浏览器打开
3. 点击"获取视频数据"按钮开始获取数据
4. 等待程序完成数据获取和处理
5. 查看结果：程序会显示获取到的视频列表，并生成JSON和HTML文件

### 4. 查看数据

- JSON数据保存在`热门视频数据.json`文件中
- HTML可视化页面保存在`视频数据.html`文件中
- 如果勾选了自动打开选项，HTML页面会自动在默认浏览器中打开

## 配置项说明

- `API_KEY`：YouTube Data API的密钥，用于访问YouTube API
- `DEFAULT_TIME_WINDOW_HOURS`：默认的时间窗口（小时），用于筛选视频发布时间
- `MAX_RESULTS`：最大结果数，指定要获取的视频数量
- `SEARCH_QUERY`：搜索关键词，默认为"slots"
- `APP_TITLE`：应用程序标题
- `WINDOW_SIZE`：窗口默认大小
- `MIN_WINDOW_WIDTH`和`MIN_WINDOW_HEIGHT`：窗口最小尺寸

## 打包应用

可以使用PyInstaller将程序打包为可执行文件。

### 基本打包命令

```
pyinstaller --name "热门视频获取工具" --windowed --add-data "generate_html_with_data.py;." 获取热门视频数据.py
```

### 参数说明

- `--name "热门视频获取工具"`: 设置打包后的应用程序名称
- `--windowed`: 创建一个不显示命令行窗口的GUI应用程序（Windows上是.pyw）
- `--icon=icon.ico`: 设置应用程序图标（如果有icon.ico文件）
- `--add-data "generate_html_with_data.py;."`: generate_html_with_data.py文件添加到打包的应用程序中，放在根目录
- `--distpath ./packaging/dist`: 指定放置打包后的应用程序的目录
- `--workpath ./packaging/build`: 指定放置所有临时工作文件的目录
- `--specpath ./packaging`: 指定存放spec文件的目录

### 更多选项（可选）

如果需要更多自定义选项，可以使用以下命令：

```
pyinstaller --name "热门视频获取工具" --windowed --icon=icon.ico --add-data "generate_html_with_data.py;." --onefile --clean --distpath ./packaging/dist --workpath ./packaging/build --specpath ./packaging 获取热门视频数据.py
```

额外选项说明：
- `--onefile`: 将所有内容打包成单个可执行文件，而不是一个目录
- `--clean`: 在构建之前清理PyInstaller缓存和临时文件

### 特定于此项目的打包命令（推荐）

考虑到项目的特殊性，以下是推荐的打包命令：

#### Windows:
```
pyinstaller --name "热门视频获取工具" --windowed --add-data "generate_html_with_data.py;." 获取热门视频数据.py
```

#### macOS:
```
pyinstaller --name "热门视频获取工具" --windowed --add-data "generate_html_with_data.py:." 获取热门视频数据.py
```

### 文件夹结构

```
项目根目录/

├── dist/   # 包含最终的可执行文件
├── build/    # 包含临时构建文件
├── 热门视频获取工具.spec  # PyInstaller规范文件
├── project/             # 项目源代码
└── 其他项目文件...
```


### 注意事项

1. 确保已安装PyInstaller：
   ```
   pip install pyinstaller
   ```

2. 如果是在macOS上打包，需要将分号改为冒号，如上面的macOS命令所示。

3. 打包完成后，可执行文件将位于`./dist`目录中。

4. 如果使用了`--onefile`选项，应用程序启动可能会稍慢，因为需要先将文件解压到临时目录。

## 注意事项

1. 需要有效的YouTube Data API密钥才能使用本工具
2. API有使用配额限制，请合理使用
3. 生成的HTML文件包含完整的视频数据，可以离线查看
4. 打包后的应用程序会在同一目录下生成JSON和HTML文件

## 开发依赖库

- googleapiclient
- tkinter
- json
- os
- sys
- datetime
- threading
- webbrowser

## 获取YouTube API密钥

1. 访问[Google Cloud Console](https://console.cloud.google.com/)
2. 创建一个新项目
3. 启用YouTube Data API v3
4. 创建API密钥
5. 将密钥复制到config.json文件中的API_KEY字段
