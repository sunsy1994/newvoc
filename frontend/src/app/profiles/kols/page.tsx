import { ProfileMaintenancePage } from "@/components/profiles/ProfileMaintenancePage";
import type { ProfilePageConfig } from "@/types/profiles";

export default function KolProfilesPage() {
  const config: ProfilePageConfig = {
    mode: "kols",
    title: "KOL画像",
    eyebrow: "Profile Maintenance",
    sampleTitle: "KOL样本导出",
    sampleMeta: "按近 N 天发帖聚合，为线下LLM标注准备样本。",
    uploadTitle: "KOL画像上传",
    uploadMeta: "上传包含 author_id 与画像字段的 Excel，系统按 author_id + profile_batch 覆盖更新。",
    listTitle: "已入库KOL画像",
    searchPlaceholder: "搜索作者、ID、KOL类型",
    exportEndpoint: "/profiles/kols/samples/export",
    uploadEndpoint: "/profiles/kols/upload",
    listEndpoint: "/profiles/kols",
    batchesEndpoint: "/profiles/kols/batches",
    sampleDays: true,
  };

  return <ProfileMaintenancePage config={config} />;
}
