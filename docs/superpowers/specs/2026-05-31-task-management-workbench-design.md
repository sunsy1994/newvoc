# 阶段1：任务管理工作台设计

## 1. 目标

阶段1只建设「任务管理」一级菜单，解决原始数据进入系统和 ETL 作业可观测的问题。

用户完成三件事即可：

1. 上传事件、内容、评论三张原始文件。
2. 触发或查看 ETL 作业。
3. 查看本次作业的输入、输出、拒绝行和结果数据。

暂不做数据资产目录、复杂 BI、AI 摘要、部门视角和用户旅程。

## 2. 技术选型

- 清洗脚本：Python，复用当前 `etl/event_voc_ods_etl.py`。
- 接口：FastAPI。
- 后端：Python。
- 数据库：PostgreSQL。
- 页面：FastAPI 服务静态 HTML/CSS/JS，第一版不引入 React。

第一版前端采用克制的数据运营后台风格：左侧菜单、顶部状态区、批次列表、文件上传区、作业结果区。页面重点是稳定、清楚、可核查。

## 3. 一级菜单与页面

一级菜单：任务管理

任务管理下第一版包含一个页面：事件VOC导入任务。

页面模块：

1. 上传原始数据
   - 展示三张模板下载入口。
   - 上传 `event_upload`、`content_upload`、`comment_upload`。
   - 上传后生成导入批次。

2. ETL 作业情况
   - 展示批次号、状态、创建时间、运行时间。
   - 展示输入行数、输出行数、拒绝行数。
   - 支持重新执行该批次 ETL。

3. 作业结果查看
   - ODS：事件、内容、评论原始上传数据。
   - DWD：事件、内容、作者、评论标准结果。
   - REL：事件-内容、作者-内容关系。
   - ADS：事件总览、日趋势、内容排行、位置分布。
   - rejected：内容拒绝行、评论拒绝行。

## 4. 后端边界

第一版后端只做本地工作台，不先做多人权限。

核心目录：

- `app/main.py`：FastAPI 应用入口。
- `app/config.py`：路径和数据库配置。
- `app/services/task_store.py`：任务批次元数据读写。
- `app/services/etl_runner.py`：调用现有 ETL 脚本并记录结果。
- `app/routers/tasks.py`：任务管理 API。
- `app/static/`：任务管理页面静态资源。

## 5. 数据存储策略

PostgreSQL 是正式方向，但为了第一版快速跑通，先采用双层设计：

1. 文件系统保存上传文件和 ETL 输出。
2. SQLite/JSON 不引入，任务元数据直接写入 PostgreSQL 兼容的数据模型；如果本机没有数据库连接，第一版使用文件型 metadata JSON 作为开发兜底。

后续接入真实 PostgreSQL 时，任务字段保持一致。

批次目录结构：

```text
runtime/tasks/<batch_id>/
  input/
    event_upload.xlsx
    content_upload.xlsx
    comment_upload.xlsx
  output/
    ods_event_upload.csv
    dwd_content.csv
    ads_event_overview.csv
    ...
  task.json
```

## 6. API

- `GET /`：打开任务管理页面。
- `GET /api/tasks`：批次列表。
- `POST /api/tasks/upload`：上传三张文件并创建批次。
- `POST /api/tasks/{batch_id}/run`：执行或重新执行 ETL。
- `GET /api/tasks/{batch_id}`：批次详情。
- `GET /api/tasks/{batch_id}/tables`：该批次可查看的数据表列表。
- `GET /api/tasks/{batch_id}/tables/{table_name}`：分页查看 CSV 表格结果。
- `GET /api/templates/{template_name}`：下载模板。

## 7. 状态定义

- `uploaded`：文件已上传，未执行 ETL。
- `running`：ETL 执行中。
- `success`：ETL 成功。
- `failed`：ETL 失败。

## 8. 第一版不做

- 不做登录权限。
- 不做定时调度。
- 不做可视化图表。
- 不做数据资产目录。
- 不做前端框架工程化。
- 不把 ODS/DWD/ADS 结果直接写入 PostgreSQL；先保留 CSV 输出，等工作台稳定后再接正式入库。

## 9. 验收标准

1. 能从页面上传三张 Excel/CSV 文件。
2. 上传后能看到一个新批次。
3. 能点击运行 ETL。
4. ETL 成功后能看到 summary 统计。
5. 能查看至少 ODS、DWD、ADS、rejected 的 CSV 表格。
6. ETL 失败时页面能显示错误信息。
7. 命令行测试通过，FastAPI 服务能启动。
