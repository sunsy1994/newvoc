import { CompetitorLibraryPage } from "@/components/competitors/CompetitorLibraryPage";
import type { CompetitorPageConfig } from "@/types/competitors";

export default function CompetitorAccountsPage() {
  const config: CompetitorPageConfig = {
    mode: "accounts",
    title: "竞品账号库",
    eyebrow: "Competitor Intelligence",
    listTitle: "竞品账号资产",
    listMeta: "展示已入库的竞品品牌、官方账号、经销商账号和内容账号。",
    searchPlaceholder: "搜索品牌、账号、账号类型",
    listEndpoint: "/competitors/accounts",
    exportEndpoint: "/competitors/accounts/export",
  };

  return <CompetitorLibraryPage config={config} />;
}
