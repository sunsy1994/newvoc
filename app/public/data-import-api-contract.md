# 数据导入接口契约

## GET /api/data-access/overview

返回数据接入总览。

## GET /api/data-import/templates

返回模板列表。

## GET /api/data-import/jobs

返回导入任务列表。

## POST /api/data-import/jobs

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
