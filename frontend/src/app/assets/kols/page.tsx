import { AssetLibraryPage } from "@/components/assets/AssetLibraryPage";
import type { AssetPageConfig } from "@/types/assets";

export default function KolAssetsPage() {
  const config: AssetPageConfig = {
    assetKey: "kols",
    title: "KOL资产",
    eyebrow: "Business Assets",
    listTitle: "KOL账号资产",
    listMeta: "展示已识别KOL账号的基础信息、发帖量、评论量和互动量。",
    searchPlaceholder: "搜索平台、KOL、作者类型",
  };

  return <AssetLibraryPage config={config} />;
}
