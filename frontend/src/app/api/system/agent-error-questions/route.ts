import { proxyAutovocGet } from "../../_autovocProxy";

export const dynamic = "force-dynamic";
export const maxDuration = 120;

export async function GET(): Promise<Response> {
  return proxyAutovocGet("/system/agent-error-questions");
}
