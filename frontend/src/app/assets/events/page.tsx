import { AssetLibraryPage } from "@/components/assets/AssetLibraryPage";
import type { AssetPageConfig } from "@/types/assets";

export default function EventAssetsPage() {
  const config: AssetPageConfig = {
    assetKey: "events",
    title: "事件资产",
    eyebrow: "Business Assets",
    listTitle: "事件资产明细",
    listMeta: "展示事件、品牌、车型、声量和互动等业务字段。",
    searchPlaceholder: "搜索事件、品牌、车型、事件类型",
  };

  return <AssetLibraryPage config={config} />;
}
