/**
 * Acceptance Criteria:
 * - Shows credential profiles on success.
 * - Shows masked fingerprint (no raw secrets).
 * - Shows status badge for each profile.
 * - Shows empty state when no credentials.
 * - Shows error state on failure.
 * - Validate button triggers validation run and shows result.
 * - No TypeScript `any`.
 */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { MemoryRouter, Route, Routes } from "react-router";
import { describe, expect, it } from "vitest";
import { FIXTURE_CLIENT, FIXTURE_PIPELINE_A } from "../../test/msw/handlers";
import { server } from "../../test/msw/server";
import { CredentialHealthPage } from "./CredentialHealthPage";

const CID = FIXTURE_CLIENT.id;
const PID = FIXTURE_PIPELINE_A.id;

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/clients/${CID}/pipelines/${PID}/credentials`]}>
        <Routes>
          <Route
            path="/clients/:clientId/pipelines/:pipelineId/credentials"
            element={<CredentialHealthPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("CredentialHealthPage", () => {
  it("shows credential profiles on success", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByText("Mock Search API Key")).toBeInTheDocument(),
    );
  });

  it("shows masked fingerprint", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/\*\*\*\*abc123/)).toBeInTheDocument(),
    );
  });

  it("shows active status badge", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText("active")).toBeInTheDocument());
  });

  it("shows empty state when no credentials", async () => {
    server.use(
      http.get(
        `http://localhost/clients/${CID}/pipelines/${PID}/credentials`,
        () => HttpResponse.json([]),
      ),
    );
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/No credentials configured/i)).toBeInTheDocument(),
    );
  });

  it("shows error state on failure", async () => {
    server.use(
      http.get(
        `http://localhost/clients/${CID}/pipelines/${PID}/credentials`,
        () => HttpResponse.json({ detail: "error" }, { status: 500 }),
      ),
    );
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/Failed to load credential profiles/i)).toBeInTheDocument(),
    );
  });

  it("shows validation result after clicking Validate", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() =>
      expect(screen.getByText("Mock Search API Key")).toBeInTheDocument(),
    );
    await user.click(screen.getByRole("button", { name: /validate/i }));
    await waitFor(() =>
      expect(screen.getByText(/Validation passed/i)).toBeInTheDocument(),
    );
  });
});
