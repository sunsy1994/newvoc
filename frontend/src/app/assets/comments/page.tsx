import { AssetLibraryPage } from "@/components/assets/AssetLibraryPage";
import type { AssetPageConfig } from "@/types/assets";

export default function CommentAssetsPage() {
  const config: AssetPageConfig = {
    assetKey: "comments",
    title: "评论资产",
    eyebrow: "Business Assets",
    listTitle: "评论资产明细",
    listMeta: "展示标准化后的评论明细资产。",
    searchPlaceholder: "搜索事件、标题、平台、用户、评论",
  };

  return <AssetLibraryPage config={config} />;
}
