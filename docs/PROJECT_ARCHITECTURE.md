# VOC 看事件项目 - 架构文档与踩坑总结

> **重要提示**: 每次开发前请先阅读本文档，避免重复踩坑！

---

## 一、项目架构概览

### 1.1 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.2.0 | 前端框架 |
| TypeScript | ~5.9.3 | 类型系统 |
| Vite | 7.2.4 | 构建工具 |
| Tailwind CSS | 3.4.19 | 样式框架 |
| Framer Motion | 12.30.0 | 动画库 |
| Recharts | 2.15.4 | 图表库 |
| shadcn/ui | - | UI 组件库 |

### 1.2 目录结构

```
app/
├── src/
│   ├── components/
│   │   ├── ui/                    # shadcn/ui 组件（50+ 组件）
│   │   ├── data/                  # 数据文件
│   │   │   ├── chartsData.ts      # 部门图表数据（5个部门）
│   │   │   └── storyLinesData.ts  # 故事线数据（5个部门）
│   │   ├── voc/                   # VOC 看事件相关
│   │   │   ├── charts/            # 通用图表组件（6个）
│   │   │   ├── market/            # 市场部专属
│   │   │   │   ├── charts/        # 市场部图表（9个）
│   │   │   │   ├── data/          # 市场部数据
│   │   │   │   ├── AIReportButton.tsx
│   │   │   │   ├── AIReportModal.tsx
│   │   │   │   ├── KPICards.tsx
│   │   │   │   ├── MarketDashboard.tsx
│   │   │   │   └── types.ts       # 类型定义
│   │   │   ├── ControlKnob.tsx    # 部门切换旋钮
│   │   │   ├── StoryLineCard.tsx  # 故事线卡片
│   │   │   ├── StoryLineList.tsx  # 故事线列表
│   │   │   ├── DepartmentCharts.tsx # 部门图表
│   │   │   ├── DepartmentTabs.tsx # 部门标签（备用）
│   │   │   └── VocViewPage.tsx    # VOC 看事件主页面
│   │   ├── Header.tsx             # 顶部导航
│   │   ├── Sidebar.tsx            # 侧边栏导航
│   │   ├── StatCard.tsx           # 统计卡片
│   │   ├── TotalProfit.tsx        # 利润图表
│   │   ├── CustomerDistribution.tsx
│   │   ├── MostDayActive.tsx
│   │   ├── RepeatCustomerRate.tsx
│   │   ├── BestSellingProducts.tsx
│   │   └── AIAssistant.tsx
│   ├── hooks/
│   │   └── use-mobile.ts          # 移动端检测
│   ├── lib/
│   │   └── utils.ts               # 工具函数
│   ├── App.tsx                    # 主应用组件
│   ├── main.tsx                   # 应用入口
│   └── index.css                  # 全局样式
├── public/
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

### 1.3 页面结构

```
App.tsx
├── Sidebar (左侧导航)
│   ├── 仪表盘 (dashboard)
│   └── VOC看事件 (voc)
└── 主内容区
    ├── Header (顶部栏，仪表盘页面)
    └── 页面内容
        ├── 仪表盘页面 (dashboard)
        │   ├── Header
        │   ├── StatCard (4个)
        │   ├── TotalProfit
        │   ├── CustomerDistribution
        │   ├── MostDayActive
        │   ├── RepeatCustomerRate
        │   ├── BestSellingProducts
        │   └── AIAssistant
        └── VOC看事件页面 (voc)
            └── VocViewPage
                ├── ControlKnob (部门切换)
                ├── StoryLineList (故事线列表)
                ├── AIReportButton (仅市场部)
                ├── AIReportModal (AI 报告弹窗)
                └── 部门内容
                    ├── 市场部: MarketDashboard
                    └── 其他部门: DepartmentCharts
```

---

## 二、踩坑总结与解决方案

### 2.1 React 19 兼容性问题

#### 问题 1: react-wordcloud 不兼容

**错误现象**: 页面白屏，无法加载

**原因**: `react-wordcloud@1.2.7` 与 React 19 不兼容

**解决方案**: 创建自定义词云组件替代

```typescript
// SimpleWordCloud.tsx - 使用纯 CSS + Framer Motion
export default function SimpleWordCloud({ data, title, getTextColor, insight }) {
  const sortedData = [...data].sort((a, b) => b.frequency - a.frequency).slice(0, 15);
  const maxFreq = sortedData[0]?.frequency || 1;

  return (
    <div className="h-[200px] flex flex-wrap items-center justify-center gap-3">
      {sortedData.map((item, index) => {
        const fontSize = 12 + (item.frequency / maxFreq) * 24;
        return (
          <motion.span
            key={item.text}
            style={{ fontSize: `${fontSize}px`, color: getTextColor(item.sentiment) }}
          >
            {item.text}
          </motion.span>
        );
      })}
    </div>
  );
}
```

**相关文件**:
- `src/components/voc/market/charts/SimpleWordCloud.tsx` (新建)
- `src/components/voc/market/charts/KeywordWordCloud.tsx` (修改)
- `src/components/voc/market/charts/NegativeWordCloud.tsx` (修改)

---

### 2.2 TypeScript 类型问题

#### 问题 1: verbatimModuleSyntax 导致类型导入错误

**错误现象**:
```
error TS1484: 'XXX' is a type and must be imported using a type-only import
```

**原因**: `tsconfig.json` 启用了 `verbatimModuleSyntax`

**解决方案**: 所有类型导入必须使用 `type` 关键字

```typescript
// ❌ 错误写法
import { KPIData, VolumeTrendData } from './types';

// ✅ 正确写法
import type { KPIData, VolumeTrendData } from './types';
```

#### 问题 2: 元组类型不匹配

**错误现象**:
```
Type 'number[]' is not assignable to type '[number, number]'
```

**原因**: 某些库（如 react-wordcloud）要求精确的元组类型

**解决方案**:
```typescript
// ❌ 错误写法
fontSizes: [14, 40],
rotationAngles: [0],

// ✅ 正确写法
fontSizes: [14, 40] as [number, number],
rotationAngles: [0, 0] as [number, number],
```

#### 问题 3: 接口属性缺失

**错误现象**:
```
error TS2353: Object literal may only specify known properties, and 'label' does not exist
```

**原因**: 数据对象包含接口未定义的属性

**解决方案**:
```typescript
// 给接口添加缺失的属性
export interface DepartmentStory {
  department: string;
  label: string;  // 添加此属性
  title: string;
  stories: StoryLine[];
}
```

---

### 2.3 Recharts 图表问题

#### 问题 1: ReferenceLine yAxisId 错误

**错误现象**:
```
Uncaught Error: Invariant failed: Could not find yAxis by id "0". Available ids are: left, right.
```

**原因**: 当图表有多个 YAxis 时，ReferenceLine 必须指定 yAxisId

**解决方案**:

```typescript
// 方法 1: 为垂直参考线指定 yAxisId
<ReferenceLine
  x={d.date}
  yAxisId="left"  // 添加此属性
  stroke="#F59E0B"
/>

// 方法 2: 使用 segment 属性（适用于散点图）
<ReferenceLine
  segment={[{ x: threshold, y: 0 }, { x: threshold, y: 100 }]}
  stroke="#E5E7EB"
/>
```

**相关文件**:
- `src/components/voc/market/charts/VolumeTrendChart.tsx`
- `src/components/voc/market/charts/ChannelQuadrantChart.tsx`
- `src/components/voc/market/charts/KOLQuadrantChart.tsx`

---

### 2.4 未使用变量警告

**错误现象**: TypeScript 编译警告

**解决方案**: 移除未使用的变量/导入

```typescript
// ❌ 错误写法
import { useState } from 'react';
const [isAnimating, setIsAnimating] = useState(false);  // 未使用

// ✅ 正确写法
// 直接移除未使用的代码
const handlePrevious = () => {
  const newIndex = selectedIndex === 0 ? data.length - 1 : selectedIndex - 1;
  onSelect(newIndex);
};
```

---

## 三、开发规范

### 3.1 类型定义规范

1. **类型文件位置**: 每个功能模块的 types.ts 应放在该模块目录下
   - 市场部: `src/components/voc/market/types.ts`
   - 通用数据: `src/components/data/chartsData.ts`

2. **类型导入**: 必须使用 `type` 关键字
   ```typescript
   import type { XXX } from './types';
   ```

3. **接口定义**: 导出的接口需要在同一文件或相关数据文件中定义

### 3.2 组件命名规范

- 图表组件: `XXXChart.tsx` (如 `VolumeTrendChart.tsx`)
- 卡片组件: `XXXCard.tsx` (如 `StatCard.tsx`)
- 列表组件: `XXXList.tsx` (如 `StoryLineList.tsx`)
- 页面组件: `XXXPage.tsx` (如 `VocViewPage.tsx`)

### 3.3 数据文件规范

1. **数据与类型分离**: 数据文件应导出类型定义
   ```typescript
   // chartsData.ts
   export interface ChartCard { ... }
   export const departmentChartsData: DepartmentCharts[] = [ ... ];
   ```

2. **常量命名**: 使用 camelCase
   ```typescript
   export const marketKPIData = ...
   export const volumeTrendData = ...
   ```

### 3.4 图表开发规范

1. **使用 ResponsiveContainer**: 所有图表必须包裹
   ```typescript
   <ResponsiveContainer width="100%" height="100%">
     <LineChart data={data} ...>
       ...
     </LineChart>
   </ResponsiveContainer>
   ```

2. **自定义 Tooltip**: 使用 Tailwind 样式
   ```typescript
   const CustomTooltip = ({ active, payload }) => {
     if (active && payload && payload.length) {
       return (
         <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
           ...
         </div>
       );
     }
     return null;
   };
   ```

3. **参考线注意事项**:
   - 有多个 YAxis 时，垂直参考线需指定 `yAxisId`
   - 或使用 `segment` 属性替代

### 3.5 动画开发规范

1. **页面过渡**: 使用 AnimatePresence
   ```typescript
   <AnimatePresence mode="wait">
     <motion.div
       key={key}
       initial={{ opacity: 0 }}
       animate={{ opacity: 1 }}
       exit={{ opacity: 0 }}
     >
       {children}
     </motion.div>
   </AnimatePresence>
   ```

2. **列表动画**: 使用 stagger
   ```typescript
   {items.map((item, index) => (
     <motion.div
       key={item.id}
       initial={{ opacity: 0, y: 20 }}
       animate={{ opacity: 1, y: 0 }}
       transition={{ delay: index * 0.1 }}
     >
       {content}
     </motion.div>
   ))}
   ```

---

## 四、常用命令

```bash
# 开发环境启动
cd app && npm run dev

# 生产构建
cd app && npm run build

# 类型检查
cd app && npx tsc --noEmit

# 代码检查
cd app && npm run lint
```

---

## 五、快速参考

### 5.1 部门数据索引

| 索引 | 部门 | 标题 |
|------|------|------|
| 0 | market (市场部) | 这次传播打爆了吗？ |
| 1 | product (产品部) | 用户喜欢我们的车吗？ |
| 2 | sales (销售部) | 用户觉得值不值？ |
| 3 | service (售后部) | 用户满意吗？ |
| 4 | pr (公关部) | 有没有危机？ |

### 5.2 关键组件路径

| 组件 | 路径 |
|------|------|
| VOC 主页面 | `src/components/voc/VocViewPage.tsx` |
| 部门切换旋钮 | `src/components/voc/ControlKnob.tsx` |
| 故事线列表 | `src/components/voc/StoryLineList.tsx` |
| 部门图表 | `src/components/voc/DepartmentCharts.tsx` |
| 市场部仪表盘 | `src/components/voc/market/MarketDashboard.tsx` |
| 市场部类型 | `src/components/voc/market/types.ts` |
| 市场部数据 | `src/components/voc/market/data/marketChartData.ts` |
| 通用图表数据 | `src/components/data/chartsData.ts` |
| 故事线数据 | `src/components/data/storyLinesData.ts` |

### 5.3 已知兼容性问题

| 库 | 版本 | 问题 | 状态 |
|---|---|---|---|
| react-wordcloud | 1.2.7 | React 19 不兼容 | ✅ 已用自定义组件替代 |
| recharts | 2.15.4 | ReferenceLine 需指定 yAxisId | ✅ 已修复 |
| framer-motion | 12.30.0 | - | ✅ 正常 |
| lucide-react | 0.562.0 | - | ✅ 正常 |

---

## 六、更新日志

### 2026-02-13
- 修复 react-wordcloud 与 React 19 兼容性问题
- 修复 Recharts ReferenceLine yAxisId 错误
- 修复 TypeScript 类型导入问题
- 创建 SimpleWordCloud 自定义词云组件
- 完善项目架构文档

---

> **文档维护**: 每次遇到新问题时，请更新本文档的"踩坑总结"部分。
