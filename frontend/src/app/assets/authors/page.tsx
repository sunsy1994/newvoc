import { AssetLibraryPage } from "@/components/assets/AssetLibraryPage";
import type { AssetPageConfig } from "@/types/assets";

export default function AuthorAssetsPage() {
  const config: AssetPageConfig = {
    assetKey: "authors",
    title: "作者资产",
    eyebrow: "Business Assets",
    listTitle: "普通作者资产",
    listMeta: "展示非KOL作者的账号信息、发帖量、评论量和互动量。",
    searchPlaceholder: "搜索平台、作者、作者类型",
  };

  return <AssetLibraryPage config={config} />;
}
