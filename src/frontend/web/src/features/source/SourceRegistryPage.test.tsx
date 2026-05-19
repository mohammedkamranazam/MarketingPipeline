/**
 * Acceptance Criteria:
 * - Shows loading state while fetching.
 * - Shows connector list on success.
 * - Shows empty state when no connectors.
 * - Shows error state on failure.
 * - No TypeScript `any`.
 */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { MemoryRouter, Route, Routes } from "react-router";
import { describe, expect, it } from "vitest";
import { FIXTURE_CLIENT, FIXTURE_PIPELINE_A } from "../../test/msw/handlers";
import { server } from "../../test/msw/server";
import { SourceRegistryPage } from "./SourceRegistryPage";

const CID = FIXTURE_CLIENT.id;
const PID = FIXTURE_PIPELINE_A.id;

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/clients/${CID}/pipelines/${PID}/sources`]}>
        <Routes>
          <Route
            path="/clients/:clientId/pipelines/:pipelineId/sources"
            element={<SourceRegistryPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("SourceRegistryPage", () => {
  it("shows connector list on success", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText("Mock Search")).toBeInTheDocument());
    expect(screen.getByText("mock_search")).toBeInTheDocument();
  });

  it("shows empty state when no connectors", async () => {
    server.use(
      http.get(
        `http://localhost/clients/${CID}/pipelines/${PID}/sources`,
        () => HttpResponse.json([]),
      ),
    );
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/No source connectors configured/i)).toBeInTheDocument(),
    );
  });

  it("shows error state on failure", async () => {
    server.use(
      http.get(
        `http://localhost/clients/${CID}/pipelines/${PID}/sources`,
        () => HttpResponse.json({ detail: "Server error" }, { status: 500 }),
      ),
    );
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/Failed to load source connectors/i)).toBeInTheDocument(),
    );
  });

  it("shows Add Connector link", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText("Add Connector")).toBeInTheDocument());
  });
});
