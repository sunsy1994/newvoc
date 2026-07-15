import { AssetLibraryPage } from "@/components/assets/AssetLibraryPage";
import type { AssetPageConfig } from "@/types/assets";

export default function ReportAssetsPage() {
  const config: AssetPageConfig = {
    assetKey: "reports",
    title: "报告资产",
    eyebrow: "Business Assets",
    listTitle: "AI 生成报告",
    listMeta: "按生成时间倒序展示事件综合报告，支持查看结构化图文报告。",
    searchPlaceholder: "搜索事件名称 / 报告版本",
  };
  return <AssetLibraryPage config={config} />;
}
