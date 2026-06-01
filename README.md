# AutoVOC Event VOC

从 0 重建后的第一阶段项目，只保留「VOC看事件」的数据链路：

```text
上传模板 -> ODS -> DWD/REL -> ADS -> 后续 API/页面
```

当前仓库只包含数据、模板、ETL 和样例结果，不包含旧前端和旧后端。

## 目录

- `schema/`：PostgreSQL 数据表设计。
- `templates/event-voc/`：事件、内容、评论三张上传模板。
- `etl/`：本地 ETL 脚本。
- `app/`：FastAPI 任务管理工作台。
- `samples/event_voc_etl_sample/`：样例输入与样例输出。
- `docs/`：当前数据链路设计文档。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动任务管理工作台

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

打开：

```text
http://127.0.0.1:8000/
```

当前一级菜单为「任务管理」，支持上传事件、内容、评论三张原始文件，运行 ETL，并查看 ODS、DWD、REL、ADS、rejected 输出表。

工作台还支持 ETL 过程透明化：

- 查看从上传文件到 PostgreSQL 落库的清理流程。
- 查看每个节点的输入表、输出表、核心规则和脚本函数。
- 查看并编辑 `etl/event_voc_ods_etl.py`。
- 保存脚本前自动备份到 `runtime/script_backups/`。
- 用当前选中的批次试跑脚本。

## 资产库

一级菜单「资产库」面向业务使用者，只展示业务字段，不展示底层技术字段。

当前包含：

- 事件资产
- 内容资产
- 评论资产
- 作者资产：非 KOL 主贴作者，展示作者主页、主贴数、收到评论数、总互动量
- KOL资产：KOL 主贴作者，后续单独维护投放画像字段
- 评论用户资产：从评论表聚合评论用户昵称、位置、评论数、参与主贴数、参与事件数

数据来自 PostgreSQL 的 `data_asset` schema，主要使用 DWD/ADS 层结果。

## PostgreSQL 落库

默认连接本地 PostgreSQL：

```text
postgresql://postgres:123456@127.0.0.1:5432/postgres
```

可用 `DATABASE_URL` 环境变量覆盖。

初始化建表：

```bash
python -m app.services.db_loader init
```

工作台执行 ETL 成功后会自动把本批次结果写入 `data_asset` schema。也可以手动加载某个 ETL 输出目录：

```bash
python -m app.services.db_loader load --output-dir <ETL输出目录> --batch-id <批次ID>
```

## 生成模板

```bash
python etl/event_voc_ods_etl.py generate-templates
```

## 跑通样例

```bash
python etl/event_voc_ods_etl.py run-sample
```

## 跑真实数据

把三张上传文件放到同一个目录：

- `event_upload.xlsx` 或 `event_upload.csv`
- `content_upload.xlsx` 或 `content_upload.csv`
- `comment_upload.xlsx` 或 `comment_upload.csv`

然后执行：

```bash
python etl/event_voc_ods_etl.py run --input-dir <你的输入目录> --output-dir <你的输出目录>
```

输出结果包括：

- ODS：原始上传表。
- DWD：事件、内容、作者、评论标准明细。
- REL：事件-内容、作者-内容关系。
- ADS：事件总览、日趋势、内容排行、评论位置分布。
