import {
  Activity,
  BarChart3,
  Bot,
  BriefcaseBusiness,
  Database,
  FileStack,
  GitBranch,
  LayoutDashboard,
  LineChart,
  MessageSquareText,
  Settings2,
  Sparkles,
  TableProperties,
  UploadCloud,
  UsersRound,
} from "lucide-react";

import type { NavigationItem } from "@/types/navigation";

export const apiBaseUrl = "/api";
export const serverApiBaseUrl = process.env.AUTOVOC_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export const navigation: NavigationItem[] = [
  {
    label: "VOC看事件",
    href: "/voc/events",
    icon: Activity,
    children: [
      { label: "市场看板", href: "/voc/events/market", icon: LayoutDashboard },
    ],
  },
  {
    label: "任务管理",
    href: "/tasks",
    icon: UploadCloud,
    children: [
      { label: "导入任务", href: "/tasks/import", icon: UploadCloud },
      { label: "ETL清理流程", href: "/tasks/flow", icon: GitBranch },
      { label: "脚本维护", href: "/tasks/scripts", icon: Settings2 },
    ],
  },
  {
    label: "资产库",
    href: "/assets",
    icon: Database,
    children: [
      { label: "事件资产", href: "/assets/events", icon: BriefcaseBusiness },
      { label: "内容资产", href: "/assets/contents", icon: FileStack },
      { label: "评论资产", href: "/assets/comments", icon: MessageSquareText },
      { label: "作者资产", href: "/assets/authors", icon: UsersRound },
      { label: "KOL资产", href: "/assets/kols", icon: Sparkles },
    ],
  },
  {
    label: "竞品动态",
    href: "/competitors",
    icon: LineChart,
    children: [
      { label: "竞品账号库", href: "/competitors/accounts", icon: TableProperties },
      { label: "竞品作品库", href: "/competitors/works", icon: BarChart3 },
    ],
  },
  {
    label: "用户画像维护",
    href: "/profiles",
    icon: Bot,
    children: [
      { label: "KOL画像", href: "/profiles/kols", icon: Sparkles },
      { label: "评论用户画像", href: "/profiles/comment-users", icon: UsersRound },
    ],
  },
];
