# LLM Weights Downloader

一个用于下载和管理大型语言模型权重的工具，支持多种来源和归档功能。

## 功能特点

- 从多种来源下载模型权重（Hugging Face、ModelScope）
- 在下载前检查模型大小
- 使用正则表达式过滤特定文件
- 将下载的模型归档为多种格式
- 跟踪下载进度和速度
- 查看下载历史

## 项目结构

项目采用标准的前后端分离架构：

```
.
├── backend/                  # 后端代码
│   ├── app/                  # 应用程序代码
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务服务
│   │   └── utils/            # 工具函数
│   ├── requirements.txt      # Python依赖
│   └── run.py                # 启动脚本
├── frontend/                 # 前端代码
│   ├── index.html            # 应用入口
│   ├── src/                  # 源代码
│   │   ├── pages/            # 页面组件
│   │   ├── TaskContext.jsx   # 任务状态管理
│   │   └── other React files
└── README.md                 # 项目说明
```

## 安装和运行

### 后端

1. 安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

2. 运行后端服务：

```bash
python run.py
```

服务将在 http://localhost:8000 上启动，API文档可在 http://localhost:8000/api/docs 访问。

### 前端

1. 安装依赖：

```bash
cd frontend
npm install
```

2. 运行开发服务器：

```bash
npm run dev
```

默认将在 http://localhost:5173 上启动。

## 环境变量

可以通过创建 `.env` 文件或设置环境变量来配置应用程序：

```
HUGGINGFACE_TOKEN=your_hf_token
MODELSCOPE_TOKEN=your_ms_token
DEFAULT_DOWNLOAD_PATH=./models
```

## 支持的归档格式

- ZIP - 最兼容的格式，适中的压缩率
- TAR - Unix磁带归档格式，无压缩
- TAR.GZ - TAR与gzip压缩，速度和大小的良好平衡
- TAR.BZ2 - TAR与bzip2压缩，比gzip更好的压缩但更慢
- TAR.XZ - TAR与xz压缩，最佳压缩但最慢

## 系统要求

- Python 3.8+
- Node.js 14+
- 足够的磁盘空间用于下载和处理大型模型文件
- 互联网连接用于从在线源下载模型 