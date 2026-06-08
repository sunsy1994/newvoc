import { ProfileMaintenancePage } from "@/components/profiles/ProfileMaintenancePage";
import type { ProfilePageConfig } from "@/types/profiles";

export default function CommentUserProfilesPage() {
  const config: ProfilePageConfig = {
    mode: "comment-users",
    title: "评论用户画像",
    eyebrow: "Profile Maintenance",
    sampleTitle: "评论样本导出",
    sampleMeta: "导出系统内 comment_user_id 与该用户全部评论，便于线下LLM打标。",
    uploadTitle: "评论画像上传",
    uploadMeta: "上传 comment_user_id、profile_batch、prompt_version 与 llm_result_json，系统计算最终用户标签并落库。",
    listTitle: "已入库评论用户画像",
    searchPlaceholder: "搜索用户、昵称、主标签",
    exportEndpoint: "/profiles/comment-users/samples/export",
    uploadEndpoint: "/profiles/comment-users/upload",
    listEndpoint: "/profiles/comment-users",
    batchesEndpoint: "/profiles/comment-users/batches",
  };

  return <ProfileMaintenancePage config={config} />;
}
