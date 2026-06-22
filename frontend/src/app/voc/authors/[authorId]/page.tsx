import { AuthorDetailPage } from "@/components/voc/AuthorDetailPage";
import { serverApiBaseUrl } from "@/config/navigation";
import type { AuthorDetailPayload } from "@/types/vocMarket";

type PageProps = {
  params: {
    authorId: string;
  };
};

async function getAuthorDetail(authorId: string): Promise<AuthorDetailPayload | null> {
  try {
    const response = await fetch(`${serverApiBaseUrl}/voc/authors/${encodeURIComponent(authorId)}/detail`, {
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as AuthorDetailPayload;
  } catch {
    return null;
  }
}

export default async function AuthorDetailRoute({ params }: PageProps) {
  const payload = await getAuthorDetail(params.authorId);

  if (!payload) {
    return (
      <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)] p-10 text-center text-sm text-[var(--theme-muted)]">
        未找到作者详情，请确认作者资产已入库。
      </div>
    );
  }

  return <AuthorDetailPage payload={payload} />;
}
