import { AssetLibraryPage } from "@/components/assets/AssetLibraryPage";
import type { AssetPageConfig } from "@/types/assets";

export default function CommentUserAssetsPage() {
  const config: AssetPageConfig = {
    assetKey: "comment_users",
    title: "评论用户资产",
    eyebrow: "Business Assets",
    listTitle: "评论用户资产",
    listMeta: "按平台、昵称和位置聚合评论用户的参与情况。",
    searchPlaceholder: "搜索平台、评论用户、位置",
  };

  return <AssetLibraryPage config={config} />;
}
