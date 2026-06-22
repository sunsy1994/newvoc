import { AutoVocHomePage } from "@/components/home/AutoVocHomePage";
import { serverApiBaseUrl } from "@/config/navigation";
import type { AutoVocHomePayload } from "@/types/autoVocHome";

async function getAutoVocHome(): Promise<AutoVocHomePayload | null> {
  try {
    const response = await fetch(`${serverApiBaseUrl}/auto-voc/home?days=30`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as AutoVocHomePayload;
  } catch {
    return null;
  }
}

export default async function AutoVocHomeRoute() {
  const payload = await getAutoVocHome();
  return <AutoVocHomePage payload={payload} />;
}
