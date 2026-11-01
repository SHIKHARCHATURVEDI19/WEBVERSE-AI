import type { ZodType } from "zod";

const apiBase = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");
const workspaceId = process.env.NEXT_PUBLIC_WORKSPACE_ID || "default";

type ErrorEnvelope = { error?: { message?: string } };

export async function apiRequest<T>(
  path: string,
  schema: ZodType<T>,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-ID": workspaceId,
      ...init?.headers,
    },
  });
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const payload = (await response.json()) as ErrorEnvelope;
      message = payload.error?.message || message;
    } catch {
      // The status-based message remains useful when the response is not JSON.
    }
    throw new Error(message);
  }
  return schema.parse(await response.json());
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}
