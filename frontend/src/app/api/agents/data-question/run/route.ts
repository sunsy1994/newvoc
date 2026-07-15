import { proxyAutovocPost } from "../../../_autovocProxy";

export const dynamic = "force-dynamic";
export const maxDuration = 120;

export async function POST(request: Request): Promise<Response> {
  return proxyAutovocPost("/agents/data-question/run", request);
}
