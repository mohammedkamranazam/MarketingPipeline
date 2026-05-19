/**
 * Acceptance Criteria:
 * - Shows loading state while fetching.
 * - Shows populated client table on success.
 * - Shows error state when the server returns 500.
 * - Shows empty state when no clients returned.
 * - No TypeScript `any`.
 */
import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";
import { http, HttpResponse } from "msw";
import { ClientListPage } from "./ClientListPage";
import { server } from "../../test/msw/server";

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <ClientListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("ClientListPage", () => {
  it("shows loading state initially", () => {
    renderPage();
    expect(screen.getByLabelText("Loading clients")).toBeInTheDocument();
  });

  it("shows client table on success", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText("tec5USA")).toBeInTheDocument());
    expect(screen.getByText("tec5usa")).toBeInTheDocument();
  });

  it("shows error state on server error", async () => {
    server.use(
      http.get("http://localhost/clients", () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 }),
      ),
    );
    renderPage();
    await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument());
  });

  it("shows empty state when no clients", async () => {
    server.use(http.get("http://localhost/clients", () => HttpResponse.json([])));
    renderPage();
    await waitFor(() =>
      expect(screen.getByText("No clients yet.")).toBeInTheDocument(),
    );
  });
});
