/**
 * Acceptance Criteria:
 * - Shows policy rules list on success.
 * - Shows empty state when no rules.
 * - Evaluating a URL shows the decision result.
 * - Shows error state on rule fetch failure.
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
import { PolicySimulatorPage } from "./PolicySimulatorPage";

const CID = FIXTURE_CLIENT.id;
const PID = FIXTURE_PIPELINE_A.id;

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/clients/${CID}/pipelines/${PID}/policy`]}>
        <Routes>
          <Route
            path="/clients/:clientId/pipelines/:pipelineId/policy"
            element={<PolicySimulatorPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("PolicySimulatorPage", () => {
  it("shows policy rules on success", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/https:\/\/allowed\.com/i)).toBeInTheDocument(),
    );
  });

  it("shows empty state when no rules", async () => {
    server.use(
      http.get(
        `http://localhost/clients/${CID}/pipelines/${PID}/policy-rules`,
        () => HttpResponse.json([]),
      ),
    );
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/No policy rules defined/i)).toBeInTheDocument(),
    );
  });

  it("shows decision result after evaluation", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() =>
      expect(screen.getByPlaceholderText(/https:\/\/example\.com/i)).toBeInTheDocument(),
    );
    await user.type(
      screen.getByPlaceholderText(/https:\/\/example\.com/i),
      "https://allowed.com/page",
    );
    await user.click(screen.getByRole("button", { name: /evaluate/i }));
    await waitFor(() =>
      expect(screen.getByText(/No rule matched|Matched rule/i)).toBeInTheDocument(),
    );
  });

  it("shows error state on rule fetch failure", async () => {
    server.use(
      http.get(
        `http://localhost/clients/${CID}/pipelines/${PID}/policy-rules`,
        () => HttpResponse.json({ detail: "error" }, { status: 500 }),
      ),
    );
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/Failed to load policy rules/i)).toBeInTheDocument(),
    );
  });
});
