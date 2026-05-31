# 阶段2：业务资产库设计

## 1. 目标

新增一级菜单「资产库」，把已经清洗并落库的事件、内容、评论、作者/KOL 以业务能理解的方式展示出来。

资产库面向业务使用者，不展示 ODS、DWD、REL、ADS 等底层概念，也不展示技术字段。

## 2. 一级菜单

左侧一级菜单：

- 任务管理
- 资产库

资产库内部子菜单：

- 事件资产
- 内容资产
- 评论资产
- 作者KOL资产

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
- 媒介形态
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

### 3.4 作者KOL资产

展示字段：

- 平台
- 作者名称
- 作者类型
- 是否KOL
- 粉丝数
- 作者主页
- 作者简介
- 内容数
- 总互动量

来源：

- `data_asset.dwd_author`
- `data_asset.dwd_content`

## 4. API

- `GET /api/assets/events?q=&limit=&offset=`
- `GET /api/assets/contents?q=&limit=&offset=`
- `GET /api/assets/comments?q=&limit=&offset=`
- `GET /api/assets/authors?q=&limit=&offset=`

返回结构统一：

```json
{
  "asset": "events",
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
- 不展示技术主键、自然键、批次ID、创建时间、更新时间。

## 6. 验收标准

1. 左侧出现一级菜单「资产库」。
2. 资产库下有四个子菜单。
3. 四类资产都能从 PostgreSQL 查询并展示业务字段。
4. 支持关键词搜索。
5. 不展示底层技术字段。
6. 全量测试通过，服务正常启动。
