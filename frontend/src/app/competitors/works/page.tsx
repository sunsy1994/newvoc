import { CompetitorLibraryPage } from "@/components/competitors/CompetitorLibraryPage";
import type { CompetitorPageConfig } from "@/types/competitors";

export default function CompetitorWorksPage() {
  const config: CompetitorPageConfig = {
    mode: "works",
    title: "竞品作品库",
    eyebrow: "Competitor Intelligence",
    listTitle: "竞品作品动态",
    listMeta: "按发布时间、品牌和账号类型筛选历史竞品作品。",
    searchPlaceholder: "搜索标题、作者、话题",
    listEndpoint: "/competitors/works",
    exportEndpoint: "/competitors/works/export",
  };

  return <CompetitorLibraryPage config={config} />;
}
