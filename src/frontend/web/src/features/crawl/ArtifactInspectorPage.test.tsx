/**
 * Tests for ArtifactInspectorPage
 */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router";
import { FIXTURE_ARTIFACT, FIXTURE_PIPELINE_A } from "../../test/msw/handlers";
import ArtifactInspectorPage from "./ArtifactInspectorPage";

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

const CLIENT_ID = FIXTURE_ARTIFACT.client_id;
const PIPELINE_ID = FIXTURE_PIPELINE_A.id;

function renderPage() {
  const qc = makeClient();
  render(
    <QueryClientProvider client={qc}>
      <MemoryRouter
        initialEntries={[`/clients/${CLIENT_ID}/pipelines/${PIPELINE_ID}/artifacts`]}
      >
        <Routes>
          <Route
            path="clients/:clientId/pipelines/:pipelineId/artifacts"
            element={<ArtifactInspectorPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  return qc;
}

describe("ArtifactInspectorPage", () => {
  it("shows loading state initially", () => {
    renderPage();
    expect(document.querySelector(".loading")).toBeInTheDocument();
  });

  it("renders the page heading", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText("Artifact Inspector")).toBeInTheDocument());
  });

  it("renders artifact from fixture", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(FIXTURE_ARTIFACT.id.slice(0, 8) + "…")).toBeInTheDocument(),
    );
    expect(screen.getByText("html_page")).toBeInTheDocument();
    expect(screen.getByText("stored")).toBeInTheDocument();
  });

  it("shows robots check panel", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText("Robots.txt Check")).toBeInTheDocument());
    expect(screen.getByPlaceholderText(/https:\/\/example\.com/)).toBeInTheDocument();
  });

  it("robots check returns allowed for normal URL", async () => {
    renderPage();
    await waitFor(() => screen.getByRole("button", { name: /check/i }));
    await userEvent.type(
      screen.getByPlaceholderText(/https:\/\/example\.com/),
      "https://example.com/page",
    );
    await userEvent.click(screen.getByRole("button", { name: /check/i }));
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(/Allowed/i),
    );
  });

  it("robots check returns blocked for /private path", async () => {
    renderPage();
    await waitFor(() => screen.getByRole("button", { name: /check/i }));
    await userEvent.type(
      screen.getByPlaceholderText(/https:\/\/example\.com/),
      "https://example.com/private/data",
    );
    await userEvent.click(screen.getByRole("button", { name: /check/i }));
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(/Blocked/i),
    );
  });

  it("expands artifact row on click to show lineage details", async () => {
    renderPage();
    await waitFor(() =>
      screen.getByText(FIXTURE_ARTIFACT.id.slice(0, 8) + "…"),
    );
    await userEvent.click(screen.getByText(FIXTURE_ARTIFACT.id.slice(0, 8) + "…"));
    await waitFor(() =>
      expect(screen.getByText(/Full ID:/i)).toBeInTheDocument(),
    );
    expect(screen.getByText(/Storage key:/i)).toBeInTheDocument();
    expect(screen.getByText(/Content hash:/i)).toBeInTheDocument();
    expect(screen.getByText(/Crawl job:/i)).toBeInTheDocument();
  });
});
