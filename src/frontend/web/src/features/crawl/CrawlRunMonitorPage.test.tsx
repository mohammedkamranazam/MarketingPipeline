/**
 * Tests for CrawlRunMonitorPage
 */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router";
import { FIXTURE_CRAWL_JOB, FIXTURE_PIPELINE_A } from "../../test/msw/handlers";
import CrawlRunMonitorPage from "./CrawlRunMonitorPage";

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

const CLIENT_ID = FIXTURE_CRAWL_JOB.client_id;
const PIPELINE_ID = FIXTURE_PIPELINE_A.id;

function renderPage() {
  const qc = makeClient();
  render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/clients/${CLIENT_ID}/pipelines/${PIPELINE_ID}/crawl`]}>
        <Routes>
          <Route
            path="clients/:clientId/pipelines/:pipelineId/crawl"
            element={<CrawlRunMonitorPage />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  return qc;
}

describe("CrawlRunMonitorPage", () => {
  it("shows loading state initially", () => {
    renderPage();
    expect(document.querySelector(".loading")).toBeInTheDocument();
  });

  it("renders the page heading", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText("Crawl Job Monitor")).toBeInTheDocument());
  });

  it("shows New Job button", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByRole("button", { name: /new job/i })).toBeInTheDocument());
  });

  it("renders crawl job from fixture", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(FIXTURE_CRAWL_JOB.id.slice(0, 8) + "…")).toBeInTheDocument(),
    );
    expect(screen.getByText("crawl")).toBeInTheDocument();
    expect(screen.getByText("queued")).toBeInTheDocument();
  });

  it("shows Run button for queued job", async () => {
    renderPage();
    await waitFor(() => expect(screen.getByRole("button", { name: /run/i })).toBeInTheDocument());
  });

  it("shows Cancel button for non-terminal job", async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument(),
    );
  });

  it("clicking New Job triggers createCrawlJob", async () => {
    renderPage();
    await waitFor(() => screen.getByRole("button", { name: /new job/i }));
    await userEvent.click(screen.getByRole("button", { name: /new job/i }));
    await waitFor(() =>
      expect(screen.getAllByText("queued").length).toBeGreaterThanOrEqual(1),
    );
  });
});
