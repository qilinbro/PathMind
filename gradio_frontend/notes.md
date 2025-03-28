# 后端 API 调用规范

本文档记录前端调用后端 API 的规范，基于test_full_flow.py的调用方式。

## 学习路径 API

### 获取已注册路径
- 路径: `/learning-paths`
- 方法: GET
- 参数: `?user_id={user_id}&enrolled=true`
- 响应: 路径对象数组

### 获取推荐路径  
- 路径: `/learning-paths`
- 方法: GET
- 参数: `?user_id={user_id}&recommended=true`
- 响应: 路径对象数组

### 获取路径详情
- 路径: `/learning-paths/{path_id}`
- 方法: GET
- 参数: `?user_id={user_id}`（可选）
- 响应: 单个路径对象，包含内容列表

### 注册路径
- 路径: `/learning-paths/enroll`
- 方法: POST
- 数据:
  ```json
  {
    "user_id": 1,
    "path_id": 1,
    "personalization_settings": {
      "preferred_content_types": ["video", "interactive"],
      "study_reminder": true
    }
  }
  ```

### 更新进度
- 路径: `/learning-paths/{path_id}/progress`
- 方法: POST
- 参数: `?user_id={user_id}`
- 数据:
  ```json
  {
    "content_id": 1,
    "progress": 75.0
  }
  ```

## 评估 API

### 获取问题
- 路径: `/assessment/questions`
- 方法: GET
- 响应: 问题对象数组

### 提交评估
- 路径: `/assessment/submit`
- 方法: POST
- 数据:
  ```json
  {
    "user_id": 1,
    "responses": [
      {
        "question_id": 1,
        "response_value": {"answer": "5"},
        "response_time": 3.5
      }
    ]
  }
  ```

### 获取学习进度
- 路径: `/assessment/progress/{user_id}`
- 方法: GET
- 响应: 学习进度对象

## 内容 API

### 获取内容
- 路径: `/content/{content_id}`
- 方法: GET
- 响应: 内容对象

## 数据库模型注意事项

### 学习路径内容关联
- 关联表名: `path_content_associations`
- 字段:
  - path_id: 外键 → learning_paths.id
  - content_id: 外键 → learning_contents.id
  - order_index: 内容顺序
  - required: 是否必修
