import { AssetLibraryPage } from "@/components/assets/AssetLibraryPage";
import type { AssetPageConfig } from "@/types/assets";

export default function ContentAssetsPage() {
  const config: AssetPageConfig = {
    assetKey: "contents",
    title: "内容资产",
    eyebrow: "Business Assets",
    listTitle: "内容资产明细",
    listMeta: "展示标准化后的主贴、视频和文章资产。",
    searchPlaceholder: "搜索事件、平台、标题、作者",
  };

  return <AssetLibraryPage config={config} />;
}
