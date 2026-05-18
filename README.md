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
- `samples/event_voc_etl_sample/`：样例输入与样例输出。
- `docs/`：当前数据链路设计文档。

## 安装依赖

```bash
pip install -r requirements.txt
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
- ADS：事件总览、日趋势、内容排行。
