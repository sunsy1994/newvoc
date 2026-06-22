# 前端技术选型与实现指导文档

## 1. 项目目标

实现一个现代 SaaS 后台页面，重点是左侧双栏导航布局。

目标视觉风格：

- 浅灰色侧边栏
- 圆角容器
- 双栏导航结构
- 左侧主导航
- 右侧子导航
- 图标 + 文本
- 胶囊形选中态
- 低对比度、轻量、类似 macOS / Notion / Linear 的后台界面风格

参考描述：

> A soft light-gray two-column sidebar navigation with rounded corners, subtle background, icon-label menu items, dark active pill for primary navigation, light active pill for secondary navigation, and a minimal SaaS dashboard layout.

---

## 2. 推荐技术栈

### 核心技术

| 模块 | 选型 |
|---|---|
| 框架 | Next.js App Router |
| 语言 | TypeScript |
| 样式 | Tailwind CSS |
| 图标 | Lucide React |
| 组件基础 | shadcn/ui，可选 |
| 状态管理 | React state，后期可接 Zustand |
| 路由高亮 | `usePathname()` |
| 包管理 | pnpm |

建议优先使用：

```txt
Next.js + TypeScript + Tailwind CSS + Lucide React
```

如果只是内部后台或单页应用，也可以使用：

```txt
Vite + React + TypeScript + Tailwind CSS
```

但本项目推荐使用 Next.js，因为后续更容易扩展登录、权限、路由、服务端数据获取和页面结构。

---

## 3. 创建项目

```bash
pnpm create next-app@latest my-dashboard --typescript --eslint --app --src-dir --import-alias "@/*"
cd my-dashboard
pnpm dev
```

安装依赖：

```bash
pnpm add lucide-react clsx tailwind-merge
```

可选：初始化 shadcn/ui：

```bash
pnpm dlx shadcn@latest init
```

---

## 4. 推荐目录结构

```txt
src/
  app/
    layout.tsx
    page.tsx
    globals.css

  components/
    layout/
      AppShell.tsx

    sidebar/
      Sidebar.tsx
      PrimaryNav.tsx
      SecondaryNav.tsx
      NavItem.tsx

  config/
    navigation.ts

  lib/
    utils.ts

  types/
    navigation.ts
```

---

## 5. 组件职责

### `AppShell.tsx`

负责页面整体布局。

```tsx
<AppShell>
  {children}
</AppShell>
```

布局结构：

```txt
body
  main app container
    Sidebar
    content area
```

---

### `Sidebar.tsx`

负责左侧整个导航容器。

包含：

```tsx
<PrimaryNav />
<SecondaryNav />
```

样式重点：

- 固定宽度
- 圆角
- 浅灰背景
- 两栏布局
- 高度撑满页面

---

### `PrimaryNav.tsx`

负责左侧主导航，例如：

```txt
Home
Messages
Integrations
Finance
Threads
Contacts
Explore
```

选中效果：

- 深色背景
- 白色文字
- 圆角胶囊

---

### `SecondaryNav.tsx`

负责右侧子导航。

根据当前主菜单显示对应的 children。

选中效果：

- 白色或更浅背景
- 深色文字
- 轻微阴影
- 圆角胶囊

---

### `NavItem.tsx`

通用导航项组件。

输入：

```ts
label
href
icon
active
variant
```

variant 可分为：

```ts
"primary" | "secondary"
```

---

## 6. 导航数据结构

创建：

```txt
src/types/navigation.ts
```

```ts
import type { LucideIcon } from "lucide-react";

export type NavigationItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: number;
  children?: NavigationChildItem[];
};

export type NavigationChildItem = {
  label: string;
  href: string;
  icon?: LucideIcon;
};
```

创建：

```txt
src/config/navigation.ts
```

```ts
import {
  Archive,
  BadgeDollarSign,
  Compass,
  Folder,
  Home,
  Inbox,
  MessageSquare,
  Network,
  Star,
  Users,
} from "lucide-react";

import type { NavigationItem } from "@/types/navigation";

export const navigation: NavigationItem[] = [
  {
    label: "Home",
    href: "/",
    icon: Home,
  },
  {
    label: "Messages",
    href: "/messages",
    icon: MessageSquare,
    badge: 2,
  },
  {
    label: "Integrations",
    href: "/integrations",
    icon: Network,
  },
  {
    label: "Finance",
    href: "/finance",
    icon: BadgeDollarSign,
  },
  {
    label: "Threads",
    href: "/threads",
    icon: Inbox,
    children: [
      {
        label: "Figrush",
        href: "/threads/figrush",
        icon: Folder,
      },
      {
        label: "Ensar System",
        href: "/threads/ensar-system",
        icon: Folder,
      },
      {
        label: "Huge Icons",
        href: "/threads/huge-icons",
        icon: Folder,
      },
    ],
  },
  {
    label: "Contacts",
    href: "/contacts",
    icon: Users,
  },
  {
    label: "Explore",
    href: "/explore",
    icon: Compass,
  },
];

export const secondaryNavigation = [
  {
    title: "Archive",
    href: "/archive",
    icon: Archive,
  },
  {
    title: "Favourite's",
    href: "/favourites",
    icon: Star,
  },
];
```

---

## 7. 工具函数

创建：

```txt
src/lib/utils.ts
```

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

---

## 8. 核心布局代码

### `src/components/layout/AppShell.tsx`

```tsx
import { Sidebar } from "@/components/sidebar/Sidebar";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-zinc-200 p-4">
      <div className="flex min-h-[calc(100vh-32px)] gap-4">
        <Sidebar />

        <main className="flex-1 rounded-[28px] bg-white p-6 shadow-sm">
          {children}
        </main>
      </div>
    </div>
  );
}
```

---

### `src/components/sidebar/Sidebar.tsx`

```tsx
import { PrimaryNav } from "@/components/sidebar/PrimaryNav";
import { SecondaryNav } from "@/components/sidebar/SecondaryNav";

export function Sidebar() {
  return (
    <aside className="w-[280px] rounded-[28px] bg-zinc-100/90 p-3 shadow-sm backdrop-blur-xl">
      <div className="grid h-full grid-cols-[122px_1fr] gap-2">
        <PrimaryNav />
        <SecondaryNav />
      </div>
    </aside>
  );
}
```

---

### `src/components/sidebar/PrimaryNav.tsx`

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navigation } from "@/config/navigation";
import { cn } from "@/lib/utils";

export function PrimaryNav() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1 pt-8">
      <div className="mb-5 px-2 text-xs font-medium text-zinc-950">
        ✦ Menu
      </div>

      {navigation.map((item) => {
        const Icon = item.icon;
        const active =
          item.href === "/"
            ? pathname === "/"
            : pathname.startsWith(item.href);

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "group flex h-8 items-center justify-between rounded-full px-2.5 text-[11px] transition",
              active
                ? "bg-zinc-950 text-white"
                : "text-zinc-600 hover:bg-white/70 hover:text-zinc-950"
            )}
          >
            <span className="flex min-w-0 items-center gap-2">
              <Icon className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{item.label}</span>
            </span>

            {item.badge ? (
              <span
                className={cn(
                  "grid h-4 min-w-4 place-items-center rounded-full px-1 text-[9px]",
                  active
                    ? "bg-white text-zinc-950"
                    : "bg-zinc-900 text-white"
                )}
              >
                {item.badge}
              </span>
            ) : null}
          </Link>
        );
      })}
    </nav>
  );
}
```

---

### `src/components/sidebar/SecondaryNav.tsx`

```tsx
"use client";

import Link from "next/link";
import { Folder, Pin } from "lucide-react";
import { usePathname } from "next/navigation";

import { navigation, secondaryNavigation } from "@/config/navigation";
import { cn } from "@/lib/utils";

export function SecondaryNav() {
  const pathname = usePathname();

  const activePrimary = navigation.find((item) => {
    if (item.href === "/") return pathname === "/";
    return pathname.startsWith(item.href);
  });

  const children = activePrimary?.children ?? [];

  return (
    <nav className="flex flex-col gap-5 border-l border-zinc-200/80 pl-3 pt-11">
      <section className="space-y-1">
        {secondaryNavigation.map((item) => {
          const Icon = item.icon;
          const active = pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex h-8 items-center gap-2 rounded-full px-2.5 text-[11px] transition",
                active
                  ? "bg-white text-zinc-950 shadow-sm"
                  : "text-zinc-500 hover:bg-white/70 hover:text-zinc-950"
              )}
            >
              <Icon className="h-3.5 w-3.5" />
              <span className="truncate">{item.title}</span>
            </Link>
          );
        })}
      </section>

      {children.length > 0 ? (
        <section className="space-y-1">
          <div className="mb-2 flex items-center justify-between px-2 text-[11px] text-zinc-500">
            <span>{activePrimary?.label}</span>
            <Pin className="h-3 w-3" />
          </div>

          {children.map((item) => {
            const Icon = item.icon ?? Folder;
            const active = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex h-8 items-center gap-2 rounded-full px-2.5 text-[11px] transition",
                  active
                    ? "bg-white text-zinc-950 shadow-sm"
                    : "text-zinc-500 hover:bg-white/70 hover:text-zinc-950"
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </section>
      ) : null}

      <section className="space-y-1">
        <div className="mb-2 px-2 text-[11px] text-zinc-500">
          Folders
        </div>

        {["Store LLC", "Dulone", "Solid", "Animations"].map((label) => {
          const href = `/folders/${label.toLowerCase().replaceAll(" ", "-")}`;
          const active = pathname === href;

          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex h-8 items-center gap-2 rounded-full px-2.5 text-[11px] transition",
                active
                  ? "bg-white text-zinc-950 shadow-sm"
                  : "text-zinc-500 hover:bg-white/70 hover:text-zinc-950"
              )}
            >
              <Folder className="h-3.5 w-3.5" />
              <span className="truncate">{label}</span>
            </Link>
          );
        })}
      </section>
    </nav>
  );
}
```

---

## 9. 接入到 App Router

### `src/app/layout.tsx`

```tsx
import type { Metadata } from "next";
import "./globals.css";

import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Modern SaaS dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
```

---

### `src/app/page.tsx`

```tsx
export default function Page() {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-zinc-950">
        Dashboard
      </h1>
      <p className="mt-2 text-sm text-zinc-500">
        This is the main content area.
      </p>
    </div>
  );
}
```

---

## 10. 视觉参数规范

### Sidebar

```txt
width: 280px
border-radius: 28px
background: zinc-100 / 90%
padding: 12px
backdrop-blur: xl
```

### Primary Nav Item

```txt
height: 32px
border-radius: full
font-size: 11px
icon-size: 14px
active-bg: zinc-950
active-text: white
```

### Secondary Nav Item

```txt
height: 32px
border-radius: full
font-size: 11px
icon-size: 14px
active-bg: white
active-shadow: sm
```

```