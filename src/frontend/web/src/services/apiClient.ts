/**
 * Acceptance Criteria:
 * - All requests include a unique X-Request-Id header.
 * - 4xx responses throw ApiError with status and parsed message.
 * - 5xx responses throw ApiError with status and generic message.
 * - JSON parse errors throw ApiError.
 * - No TypeScript `any`.
 */

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function requestId(): string {
  return crypto.randomUUID();
}

async function parseError(res: Response): Promise<ApiError> {
  let message = `HTTP ${res.status}`;
  try {
    const body = (await res.json()) as { detail?: string };
    if (typeof body.detail === "string") message = body.detail;
  } catch {
    // use default message
  }
  return new ApiError(res.status, message);
}

// Resolved at build time by Vite; also set via vitest `env` config for tests.
export const API_BASE: string =
  (import.meta.env as Record<string, string | undefined>)["VITE_API_BASE"] ?? "";

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Request-Id": requestId(),
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    throw await parseError(res);
  }

  if (res.status === 204) {
    return undefined as unknown as T;
  }

  try {
    return (await res.json()) as T;
  } catch {
    throw new ApiError(res.status, "Invalid JSON response");
  }
}
