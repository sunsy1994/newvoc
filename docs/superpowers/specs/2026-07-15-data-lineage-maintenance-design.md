# AutoVOC 数据血缘维护设计

## 目标

在系统管理中新增“数据血缘维护”，让业务人员和开发人员能够追溯重要指标、规则结论、LLM 标签和 AI 总结的来源、生成方式及消费入口，避免随着看板和 Agent 能力增长出现口径混乱。

第一版采用业务输出级血缘：登记业务真正展示或被 Agent 使用的指标、规则、标签和结论，并向上追溯到必要的表和字段。第一版不扫描数据库全部字段，不记录每次 Agent 运行实例。

## 核心原则

- 每个重要数字、标签和结论都应说明来源、生成逻辑、LLM 参与情况和下游用途。
- 系统内置技术定义由代码管理，后台主要维护业务说明、负责人、状态和人工关系。
- 血缘目录不得改变现有指标、看板或 Agent 的计算行为。
- 第一版保持轻量，不引入图数据库、代码自动解析和复杂审批流程。

## 生成方式分类

血缘对象使用以下生成方式：

- `raw_fact`：上传或采集后直接进入数据层的原始事实；
- `direct_aggregation`：通过 `COUNT`、`SUM` 等直接聚合得到的指标；
- `derived_metric`：通过明确公式计算得到的派生指标；
- `rule_judgement`：通过 Python 或 SQL 阈值规则得到的业务判断；
- `llm_label`：LLM 根据 Prompt 对内容生成的结构化标签；
- `llm_summary`：LLM 消费指标和证据后生成的综合结论；
- `consumer_only`：只消费其他对象的看板、Tool 或 Agent 入口。

## 数据模型

第一版使用统一节点表和统一关系表。

### 血缘节点

表名：`data_asset.system_lineage_node`

节点类型：

- `source_field`：必要的来源表或字段；
- `metric`：直接聚合或派生指标；
- `rule`：业务规则结论；
- `llm_label`：LLM 打标结果；
- `ai_summary`：AI 综合内容；
- `dashboard`：看板消费入口；
- `agent_tool`：Agent Tool；
- `agent_output`：Agent 最终产出。

字段：

| 字段 | 说明 |
|---|---|
| `lineage_id` | 自增主键 |
| `lineage_code` | 稳定唯一编码，系统节点不可修改 |
| `lineage_name` | 中文名称 |
| `node_kind` | 节点类型 |
| `generation_type` | 生成方式 |
| `business_domain` | 市场、产品、销售或公共 |
| `business_definition` | 业务口径说明 |
| `calculation_logic` | SQL、公式或规则说明 |
| `implementation_ref` | 表字段、Python 函数或代码位置 |
| `prompt_scene` | 涉及 LLM 时对应的提示词场景 |
| `owner` | 负责人 |
| `status` | `draft`、`active` 或 `deprecated` |
| `is_system` | 是否由代码种子管理 |
| `created_time` | 创建时间 |
| `updated_time` | 最后更新时间 |

### 血缘关系

表名：`data_asset.system_lineage_edge`

字段：

| 字段 | 说明 |
|---|---|
| `edge_id` | 自增主键 |
| `upstream_code` | 上游节点编码 |
| `downstream_code` | 下游节点编码 |
| `relation_type` | 关系类型 |
| `relation_description` | 业务关系说明 |
| `is_system` | 是否由代码种子管理 |
| `created_time` | 创建时间 |
| `updated_time` | 最后更新时间 |

关系类型：

- `depends_on`：一般依赖；
- `aggregates_to`：直接聚合生成；
- `calculates_to`：公式计算生成；
- `rules_to`：规则判断生成；
- `labels_to`：LLM 打标生成；
- `consumed_by`：被看板或 Tool 使用；
- `summarized_by`：被 Agent 总结使用。

关系表对 `(upstream_code, downstream_code, relation_type)` 建立唯一约束。上游和下游必须引用已存在节点，禁止直接自引用。

## 代码绑定与种子数据

新增独立的血缘种子定义，包含 `LINEAGE_NODE_SEEDS` 和 `LINEAGE_EDGE_SEEDS`。系统首次访问血缘接口时创建表并执行幂等种子同步。

同步规则：

- 不存在的系统节点和系统关系执行插入；
- 已存在的系统节点只同步名称、节点类型、生成方式、技术逻辑、实现位置和 Prompt 场景；
- 保留后台维护的业务口径、负责人和状态；
- 不覆盖人工节点和人工关系；
- 种子同步不得修改现有指标计算代码。

第一批种子覆盖：

- 事件、内容、评论的必要来源字段；
- 帖子数、评论数、总声量、总互动量；
- 正向率、负向率、中高购买信号率；
- 峰值贡献率、集中爆发、KOL 带动；
- 评论情绪、购买信号、产品关注点标签；
- 产品机会点、风险点、惊喜点；
- 市场、产品、销售看板；
- 问数、问答、报告、洞察 Agent 的主要 Tool 和产出。

## 后台入口

系统管理新增菜单：

```text
数据血缘维护
/system/data-lineage
```

## 页面结构

### 概览

页面顶部显示：

- 血缘节点数；
- 业务指标数；
- 规则判断数；
- LLM 标签数；
- AI 总结数；
- 未完善口径数。

### 血缘资产列表

表格列：

- 名称；
- 节点类型；
- 生成方式；
- 业务域；
- 是否涉及 LLM；
- 上游数量；
- 下游数量；
- 状态；
- 查看操作。

支持按名称、节点类型、业务域、生成方式和状态筛选。

### 血缘详情

点击节点后打开详情抽屉，包含：

1. 口径信息：业务定义、生成方式、计算逻辑、实现位置、Prompt 场景、负责人和状态；
2. 三列血缘链路：上游来源、当前对象、下游消费；
3. 关系维护：添加上游、添加下游、选择关系类型、填写关系说明和删除人工关系。

链路中的节点可以继续点击查看详情。第一版使用三列链路，不引入复杂图形库。

## 编辑权限

系统节点允许修改：

- 业务口径说明；
- 负责人；
- 状态；
- 补充说明型关系。

系统节点禁止修改：

- `lineage_code`；
- `node_kind`；
- `generation_type`；
- `implementation_ref`；
- 其他由代码种子维护的技术字段。

人工节点可以完整编辑。系统节点和系统关系不能删除，只能将节点状态调整为 `deprecated`。人工关系允许删除。

## API

### `GET /api/system/data-lineage`

支持 `q`、`node_kind`、`business_domain`、`generation_type` 和 `status` 筛选，返回概览统计和节点列表。

### `GET /api/system/data-lineage/{lineage_code}`

返回当前节点、直接上游、直接下游、相关边和可选关联节点。

### `POST /api/system/data-lineage/nodes`

创建人工节点。拒绝重复编码和非法枚举。

### `PUT /api/system/data-lineage/nodes/{lineage_code}`

更新节点。系统节点只接受业务口径、负责人和状态字段。

### `POST /api/system/data-lineage/edges`

创建人工关系。拒绝不存在节点、直接自引用和重复关系。

### `DELETE /api/system/data-lineage/edges/{edge_id}`

只允许删除人工关系。系统关系返回明确错误。

## 错误与降级

- 数据库表不存在时由服务幂等创建，不要求用户手工执行建表脚本；
- 种子同步失败时接口返回明确错误，不返回伪造空目录；
- 查询不存在节点时返回 `404`；
- 非法枚举、重复节点、自引用和删除系统关系返回业务错误；
- 前端加载失败时保留筛选和当前页面，展示可重试错误；
- 详情抽屉加载失败不清空列表；
- 数据血缘功能失败不得影响现有看板和 Agent 接口。

## 验收标准

- 系统管理可以进入数据血缘维护页面；
- 页面能够区分直接聚合、派生指标、规则判断、LLM 标签和 LLM 总结；
- 能从重要指标查看必要来源和看板、Tool、Agent 消费入口；
- 可以维护业务口径、负责人、状态和人工关系；
- 系统节点技术字段和系统关系受到保护；
- 种子同步幂等，重复访问不会产生重复节点或关系；
- 关键种子包含四个 Agent 的主要输入或产出；
- 原有看板、报告资产和四个 Agent 行为不受影响；
- 后端服务、API、前端页面和保护规则具有自动化测试。

## 非目标

- 不建立字段级全库数据目录；
- 不解析整个代码库自动生成血缘；
- 不记录每次 Agent 运行实例；
- 不引入图数据库；
- 不提供复杂循环依赖检测；
- 不提供审批流、完整版本审计和角色权限；
- 不修改现有指标、规则或 LLM 打标逻辑。
