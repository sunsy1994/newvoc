# 数据导入接口契约

## 1. 总览接口

### `GET /api/data-access/overview`

返回数据接入总览，包含：
- summary
- sources
- templates
- jobs
- postgres

响应示例：

```json
{
  "summary": [
    { "id": "sources", "label": "数据源", "value": "4", "hint": "Excel / 文本统一进站", "tone": "blue" }
  ],
  "sources": [],
  "templates": [],
  "jobs": [],
  "postgres": {
    "schemaName": "data_asset",
    "currentDatabase": "autovoc",
    "tables": ["dwd_event", "dwd_content"]
  }
}
```

## 2. 模板接口

### `GET /api/data-import/templates`

返回所有模板配置。

说明：
- 模板下载默认提供 `xlsx`
- 模板列头使用中文
- 后端会把中文列头映射到数据库英文字段

### `GET /api/data-import/templates/:templateId/download`

下载指定模板文件。

建议返回：
- 文件流
- `Content-Disposition: attachment`

## 3. 任务接口

### `GET /api/data-import/jobs`

返回最近导入任务列表。

### `POST /api/data-import/jobs`

创建导入任务。

请求体：

```json
{
  "sourceKey": "content",
  "templateId": "tpl-content",
  "fileName": "content_20260318.xlsx",
  "fileFormat": "xlsx",
  "operator": "local-admin"
}
```

响应体：

```json
{
  "jobId": "job-20260318-008",
  "accepted": true,
  "message": "任务已创建，进入模板校验队列。"
}
```

## 4. 后端处理建议

`POST /api/data-import/jobs` 建议流程：

1. 校验模板是否存在
2. 校验文件扩展名是否匹配模板
3. 生成导入任务记录
4. 读取 Excel / CSV / TXT
5. 校验必填字段
6. 补齐统一主键
7. 写入 `dwd_*` 和 `rel_*`
8. 回写任务状态、写入行数、拒绝行数、异常说明

## 5. 主键生成建议

- `event_id`
  手工维护优先

- `content_id`
  平台原始内容ID优先；若缺失，则使用 `platform + source_url hash`

- `comment_id`
  平台原始评论ID优先；若缺失，则使用 `content_id + comment_text hash`

- `account_id`
  平台原始账号ID优先；若缺失，则使用 `platform + nickname hash`

## 6. 导入口径说明

- 评论中的 `观点标签`、`意图标签`、`情感标签`、`用户画像`、`用户阶段`、`心智标签`
  默认视为外部已标注结果，直接导入 `dwd_comment`

- 账号中的 `用户画像`、`用户阶段`、`画像标签`
  默认视为外部已标注结果，直接导入 `dwd_account`

- 系统当前主要负责：
  - 模板校验
  - 主键补齐
  - 明细入库
  - pandas 聚合计算

- 系统当前不负责：
  - 对评论重新做 AI 标签识别
  - 对用户重新做 AI 画像识别
