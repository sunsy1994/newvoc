const backendApiBaseUrl = process.env.AUTOVOC_API_BASE_URL ?? "http://127.0.0.1:8000/api";

function backendUrl(path: string): string {
  return `${backendApiBaseUrl}${path}`;
}

function proxyResponse(response: Response): Response {
  return new Response(response.body, {
    status: response.status,
    headers: {
      "content-type": response.headers.get("content-type") ?? "application/json; charset=utf-8",
    },
  });
}

export async function proxyAutovocPost(path: string, request: Request): Promise<Response> {
  try {
    const response = await fetch(backendUrl(path), {
      method: "POST",
      headers: { "content-type": request.headers.get("content-type") ?? "application/json" },
      body: await request.text(),
      cache: "no-store",
    });
    return proxyResponse(response);
  } catch (error) {
    return Response.json(
      { detail: error instanceof Error ? error.message : "AutoVOC backend request failed" },
      { status: 502 },
    );
  }
}

export async function proxyAutovocGet(path: string): Promise<Response> {
  try {
    const response = await fetch(backendUrl(path), { cache: "no-store" });
    return proxyResponse(response);
  } catch (error) {
    return Response.json(
      { detail: error instanceof Error ? error.message : "AutoVOC backend request failed" },
      { status: 502 },
    );
  }
}
