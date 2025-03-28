# PathMind 学习路径平台

一个自适应学习平台，提供个性化学习路径规划和自适应测试功能。

## 项目结构

```
PathMind/
├── backend/        # FastAPI 后端
└── gradio_front2/  # Gradio 前端界面
```

## 开发环境设置

### 先决条件

- Python 3.11 或更高版本
- UV 包管理器（推荐）或 pip

### 安装依赖

```bash
# 使用 UV 安装依赖
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

## 运行应用

### 启动后端

```bash
cd Rooed/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端

```bash
cd Rooed/gradio_front2
python app.py
```

## API 文档

启动后端服务器后，可以在以下地址访问 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发说明

- 前端使用 Gradio 框架构建，提供可视化界面
- 后端基于 FastAPI 构建 RESTful API
- 学习路径功能位于 `gradio_front2/pages/learning_path.py`
- 自适应测试功能位于 `gradio_front2/pages/adaptive_test.py`