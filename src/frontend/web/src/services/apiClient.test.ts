/**
 * Acceptance Criteria:
 * - apiFetch returns parsed JSON on success.
 * - apiFetch throws ApiError with status and detail on 4xx.
 * - apiFetch throws ApiError on 5xx.
 * - apiFetch handles 204 No Content without parsing.
 * - apiFetch throws ApiError on JSON parse failure.
 * - No TypeScript `any`.
 */
import { describe, expect, it } from "vitest";
import { apiFetch, ApiError } from "./apiClient";
import { http, HttpResponse } from "msw";
import { server } from "../test/msw/server";

describe("apiFetch", () => {
  it("returns JSON on 200", async () => {
    server.use(http.get("http://localhost/test", () => HttpResponse.json({ ok: true })));
    const result = await apiFetch<{ ok: boolean }>("/test");
    expect(result.ok).toBe(true);
  });

  it("throws ApiError on 404 with detail", async () => {
    server.use(
      http.get("http://localhost/test-404", () =>
        HttpResponse.json({ detail: "Not found" }, { status: 404 }),
      ),
    );
    await expect(apiFetch("/test-404")).rejects.toMatchObject({
      status: 404,
      message: "Not found",
    });
  });

  it("throws ApiError on 500", async () => {
    server.use(
      http.get("http://localhost/test-500", () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 }),
      ),
    );
    const err = await apiFetch("/test-500").catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect((err as ApiError).status).toBe(500);
  });

  it("handles 204 No Content", async () => {
    server.use(
      http.delete("http://localhost/test-204", () => new HttpResponse(null, { status: 204 })),
    );
    const result = await apiFetch("/test-204", { method: "DELETE" });
    expect(result).toBeUndefined();
  });
});
