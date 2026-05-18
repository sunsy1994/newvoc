# FastAPI Backend

## 安装

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 环境变量

可选 `.env`：

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/autovoc
```

## 启动

```bash
uvicorn app.main:app --reload --port 8000
```

前端开发环境默认通过 Vite 代理 `/api` 到 `http://127.0.0.1:8000`。

如果前端不走 Vite 代理，也可以在 `app/.env.local` 里设置：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 已实现接口

- `GET /api/data-access/overview`
- `GET /api/data-import/templates`
- `GET /api/data-import/jobs`
- `GET /api/data-import/templates/{template_id}/download`
- `POST /api/data-import/jobs`
- `GET /api/data-calc/graph`
- `GET /api/data-calc/tasks`
- `GET /api/data-calc/tasks/{task_id}`
- `POST /api/data-calc/tasks/{task_id}/run`

`POST /api/data-import/jobs` 使用 `multipart/form-data`：

- `source_key`
- `template_id`
- `operator`
- `file`

模板特点：
- 下载格式默认是 `xlsx`
- 列头使用中文
- 后端导入时会自动映射到数据库英文列名
- 评论和账号中的画像/标签字段默认视为外部已标注结果，系统不重复做 AI 标注

## 数据计算任务

任务脚本位于：

```bash
backend/app/tasks/
```

当前已提供 4 个 pandas 示例任务：
- `event_asset_overview.py`
- `author_event_summary.py`
- `content_comment_profile.py`
- `kol_event_summary.py`
