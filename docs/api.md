# 后端 API 文档

本文档基于 `backend/app` 下的 FastAPI 应用代码整理，列出了所有可用接口、路径、方法、请求参数、请求示例和响应示例。

---

## 全局接口

### GET /api/v1  
**描述**  
API 根路径，返回服务名称、版本、描述及各子路由入口。  

**请求示例**  
```
GET http://{host}:{port}/api/v1
```

**响应示例**  
```json
{
  "name": "YourProjectName",
  "version": "1.0",
  "description": "学习路径平台API",
  "endpoints": {
    "assessment": "/api/v1/assessment",
    "content": "/api/v1/content",
    "learning_paths": "/api/v1/learning-paths",
    "analytics": "/api/v1/analytics"
  }
}
```

---

### GET /health  
**描述**  
健康检查，确认服务在线。  

**请求示例**  
```
GET http://{host}:{port}/health
```

**响应示例**  
```json
{
  "status": "ok",
  "api_version": "1.0"
}
```

---

### GET /api-status  
**描述**  
检查第三方 AI 服务（智谱 AI）连接状态。  

**请求示例**  
```
GET http://{host}:{port}/api-status
```

**响应示例**  
```json
{
  "api_key_configured": true,
  "client_available": true,
  "model": "gpt-3.5",
  "timeout": 30,
  "environment": "development"
}
```

---

## Assessment（评估）接口 `/api/v1/assessment`

### GET /api/v1/assessment/questions  
**描述**  
获取所有评估问题列表。  

**响应模型**  
`List[QuestionSchema]`  

**响应示例**  
```json
[
  {
    "id": 1,
    "text": "你喜欢哪种学习方式？",
    "options": ["视觉", "听觉", "动手"]
  }
]
```

---

### POST /api/v1/assessment/questions  
**描述**  
创建新的评估问题。  

**请求模型**  
```json
{
  "text": "问题文本",
  "options": ["选项A", "选项B"]
}
```

**响应模型**  
`QuestionSchema`  

**响应示例**  
```json
{
  "id": 42,
  "text": "问题文本",
  "options": ["选项A", "选项B"]
}
```

---

### POST /api/v1/assessment/submit  
**描述**  
提交用户评估答案，计算评估结果。  

**请求模型**  
```json
{
  "user_id": 123,
  "responses": [
    {"question_id": 1, "answer": "视觉"},
    {"question_id": 2, "answer": "听觉"}
  ]
}
```

**响应模型**  
`AssessmentResponse`  

**响应示例**  
```json
{
  "user_id": 123,
  "score": 85,
  "result": "视觉学习者"
}
```

---

### GET /api/v1/assessment/user/{user_id}/history  
**描述**  
查询某用户的历史评估记录。  

**路径参数**  
- `user_id` (int): 用户 ID  

**响应模型**  
`List[dict]`  

---

### GET /api/v1/assessment/assessment/{assessment_id}  
**描述**  
获取单次评估详情（包括问题和答案）。  

**路径参数**  
- `assessment_id` (int): 评估 ID  

**响应模型**  
`dict`  

---

### GET /api/v1/assessment/progress/{user_id}  
**描述**  
获取用户学习进度摘要。  

**路径参数**  
- `user_id` (int): 用户 ID  

**响应模型**  
`dict`  

---

### POST /api/v1/assessment/adaptive-test  
**描述**  
基于 AI 生成自适应测试题。  

**请求模型**  
```json
{
  "user_id": 123,
  "topic": "Python",
  "difficulty": "中级"
}
```

**响应模型**  
`AdaptiveTestResult`  

---

## Content（学习内容）接口 `/api/v1/content`

### GET /api/v1/content  
**描述**  
获取所有学习内容列表。  
**响应模型**  
`List[ContentResponse]`

---

### POST /api/v1/content  
**描述**  
创建新学习内容。  
**请求模型**  
```json
{
  "title": "FastAPI 入门",
  "body": "FastAPI 是一个 ...",
  "tags": ["Python", "Web"]
}
```
**响应模型**  
`ContentResponse`

---

### GET /api/v1/content/{content_id}  
**描述**  
获取单个内容详情。  
**路径参数**  
- `content_id` (int)

**响应模型**  
`ContentResponse`

---

### PUT /api/v1/content/{content_id}  
**描述**  
更新指定内容。  
**请求模型**  
同 POST /api/v1/content  
**响应模型**  
`ContentResponse`

---

### DELETE /api/v1/content/{content_id}  
**描述**  
删除指定内容。  
**响应示例**  
```json
{"message": "Deleted"}
```

---

## Learning Paths（学习路径）接口 `/api/v1/learning-paths`

### POST /api/v1/learning-paths  
**描述**  
创建新学习路径。  
**请求模型**  
```json
{
  "title": "全栈开发",
  "description": "从零开始学全栈",
  "steps": [/*...*/]
}
```
**响应状态**  
201 Created

---

### POST /api/v1/learning-paths/enroll  
**描述**  
用户报名学习路径。  
**请求模型**  
```json
{
  "user_id": 123,
  "path_id": 10
}
```

---

### GET /api/v1/learning-paths/{path_id}  
**描述**  
获取学习路径详情。  
**路径参数**  
- `path_id` (int)

---

### POST /api/v1/learning-paths/{path_id}/progress  
**描述**  
更新用户路径进度。  
**请求模型**  
```json
{
  "user_id": 123,
  "completed_steps": [1,2]
}
```

---

### GET /api/v1/learning-paths/recommended  
**描述**  
获取 AI 推荐路径列表。  
**响应模型**  
`List[Dict[str, Any]]`

---

## Analytics（分析）接口 `/api/v1/analytics`

- **GET /api/v1/analytics/summary**  
  返回全局学习数据汇总。  
- **GET /api/v1/analytics/user/{user_id}**  
  返回单个用户分析数据。

---

## Users（用户）接口 `/api/v1/users`

- **POST /api/v1/users/register**  
  用户注册。  
- **POST /api/v1/users/login**  
  用户登录，返回 Token。  
- **GET /api/v1/users/{user_id}**  
  获取用户信息。

> **备注**  
> - 全接口均使用 JSON 格式请求/响应。  
> - 若启用认证，请在 `Authorization: Bearer <token>` 头中携带。  
> - 更多字段和校验规则，请参考 `backend/app/api/v1/schemas` 中的 Pydantic 定义。  
> - Swagger UI 文档地址：`/docs`，OpenAPI JSON：`/api/v1/openapi.json`