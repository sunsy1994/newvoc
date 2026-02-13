# Shopeers Dashboard 技术规划

## 组件清单

### shadcn/ui 组件
- Button - 按钮组件
- Card - 卡片容器
- Avatar - 用户头像
- Badge - 徽章标签
- Table - 产品表格
- DropdownMenu - 下拉菜单
- Tooltip - 提示框
- Progress - 进度条
- Separator - 分割线

### 第三方组件
无需额外第三方组件

### 自定义组件
1. **Sidebar** - 侧边栏导航
2. **Header** - 顶部导航栏
3. **StatCard** - 统计卡片
4. **LineChart** - 折线图 (使用 Recharts)
5. **BarChart** - 柱状图 (使用 Recharts)
6. **RadialChart** - 环形图 (使用 Recharts)
7. **CustomerDistribution** - 客户分布进度条
8. **ProductTable** - 产品表格

---

## 动画实现规划

| 动画 | 库 | 实现方式 | 复杂度 |
|------|-----|----------|--------|
| 页面加载序列 | Framer Motion | AnimatePresence + stagger | 中 |
| 侧边栏滑入 | Framer Motion | initial/animate x | 低 |
| 统计卡片入场 | Framer Motion | staggerChildren | 低 |
| 数字计数动画 | Framer Motion | useMotionValue + animate | 中 |
| 卡片hover效果 | CSS/Tailwind | hover:translate-y + shadow | 低 |
| 折线图绘制 | Recharts | animationDuration | 低 |
| 柱状图升起 | Recharts | animationBegin + animationDuration | 低 |
| 圆环绘制 | Recharts | animationBegin + animationDuration | 低 |
| 进度条动画 | Framer Motion | initial/animate width | 低 |
| 菜单展开收起 | Framer Motion | AnimatePresence height | 中 |

---

## 项目结构

```
app/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui 组件
│   │   ├── Sidebar.tsx      # 侧边栏
│   │   ├── Header.tsx       # 顶部栏
│   │   ├── StatCard.tsx     # 统计卡片
│   │   ├── TotalProfit.tsx  # 利润图表
│   │   ├── CustomerDistribution.tsx  # 客户分布
│   │   ├── MostDayActive.tsx         # 活跃时段
│   │   ├── RepeatCustomerRate.tsx    # 复购率
│   │   ├── BestSellingProducts.tsx   # 热销产品
│   │   └── AIAssistant.tsx           # AI助手
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── index.html
├── package.json
└── tailwind.config.js
```

---

## 依赖安装

```bash
# 动画库
npm install framer-motion

# 图表库
npm install recharts

# 图标库
npm install lucide-react
```

---

## 技术要点

### 1. 响应式布局
- 使用 Tailwind CSS 的 grid 系统
- 断点: lg (1024px), md (768px)
- 侧边栏在 md 以下收起

### 2. 图表配置
- 使用 Recharts 的 ResponsiveContainer 实现响应式
- 自定义 tooltip 样式
- 渐变色填充

### 3. 动画性能
- 使用 transform 和 opacity 属性
- will-change 优化
- 减少重绘重排

### 4. 状态管理
- 使用 React useState 管理本地状态
- 侧边栏展开/收起状态
- 下拉菜单状态
