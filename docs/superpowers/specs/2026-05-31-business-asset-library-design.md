# 阶段2：业务资产库设计

## 1. 目标

新增一级菜单「资产库」，把已经清洗并落库的事件、内容、评论、作者、KOL、评论用户，以业务能理解的方式展示出来。

资产库面向业务使用者，不展示 ODS、DWD、REL、ADS 等底层概念，也不展示技术主键、自然键、批次 ID、创建时间、更新时间等技术字段。

## 2. 菜单结构

左侧一级菜单：

- 任务管理
- 资产库

资产库内部子菜单：

- 事件资产
- 内容资产
- 评论资产
- 作者资产
- KOL资产
- 评论用户资产

## 3. 字段范围

### 3.1 事件资产

展示字段：

- 事件名称
- 事件类型
- 品牌
- 车型
- 开始时间
- 结束时间
- 状态
- 内容数
- 评论数
- 作者数
- KOL内容数
- 总互动量

来源：

- `data_asset.ads_event_overview`

### 3.2 内容资产

展示字段：

- 所属事件
- 平台
- 标题
- 内容类型
- 媒介形式
- 作者名称
- 是否KOL
- 发布时间
- 点赞数
- 评论数
- 分享数
- 收藏数
- 总互动量
- 原始链接

来源：

- `data_asset.dwd_content`
- `data_asset.dwd_event`
- `data_asset.dwd_author`

### 3.3 评论资产

展示字段：

- 所属事件
- 所属内容标题
- 平台
- 位置
- 评论作者昵称
- 评论正文
- 评论时间
- 点赞数
- 回复数

来源：

- `data_asset.dwd_comment`
- `data_asset.dwd_content`
- `data_asset.dwd_event`

### 3.4 作者资产

作者资产只展示非 KOL 的主贴作者。KOL 会进入独立的 KOL资产，避免后期画像字段混在一起。

展示字段：

- 平台
- 作者名称
- 作者类型
- 粉丝数
- 作者主页
- 作者简介
- 主贴数
- 收到评论数
- 总互动量

来源：

- `data_asset.dwd_author`
- `data_asset.dwd_content`
- `data_asset.dwd_comment`

过滤规则：

- `is_kol = false` 或 `is_kol IS NULL`

### 3.5 KOL资产

KOL资产只展示主贴作者中明确标记为 KOL 的作者，后续用于维护投放画像、内容风格、粉丝画像、适配车型等字段。

展示字段：

- 平台
- 作者名称
- 作者类型
- 粉丝数
- 作者主页
- 作者简介
- 主贴数
- 收到评论数
- 总互动量

来源：

- `data_asset.dwd_author`
- `data_asset.dwd_content`
- `data_asset.dwd_comment`

过滤规则：

- `is_kol = true`

### 3.6 评论用户资产

评论用户资产来自评论表聚合。由于多数渠道只能提供昵称，第一版不做跨平台、跨渠道用户打通，只按平台 + 评论用户昵称 + 位置聚合。

展示字段：

- 平台
- 评论用户昵称
- 位置
- 评论数
- 参与主贴数
- 参与事件数
- 获赞数
- 回复数
- 最近评论时间

来源：

- `data_asset.dwd_comment`
- `data_asset.dwd_content`

## 4. API

- `GET /api/assets/events?q=&limit=&offset=`
- `GET /api/assets/contents?q=&limit=&offset=`
- `GET /api/assets/comments?q=&limit=&offset=`
- `GET /api/assets/authors?q=&limit=&offset=`
- `GET /api/assets/kols?q=&limit=&offset=`
- `GET /api/assets/comment_users?q=&limit=&offset=`

返回结构统一：

```json
{
  "asset": "events",
  "label": "事件资产",
  "total": 1,
  "columns": [{"key": "event_name", "label": "事件名称"}],
  "rows": []
}
```

## 5. 第一版不做

- 不做资产编辑。
- 不做删除。
- 不做高级筛选器。
- 不做导出。
- 不做评论用户跨平台身份合并。
- 不展示底层技术主键、自然键、批次 ID、创建时间、更新时间。

## 6. 验收标准

1. 左侧出现一级菜单「资产库」。
2. 资产库下有六个子菜单。
3. 六类资产都能从 PostgreSQL 查询并展示业务字段。
4. 作者资产和 KOL资产分开展示。
5. 评论用户资产展示评论数、参与主贴数、参与事件数等聚合指标。
6. 支持关键词搜索。
7. 不展示底层技术字段。
8. 全量测试通过，服务正常启动。
