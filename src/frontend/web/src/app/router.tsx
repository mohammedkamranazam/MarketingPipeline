/**
 * Acceptance Criteria:
 * - Routes include /clients, /clients/new, /clients/:clientId,
 *   /clients/:clientId/settings, /clients/:clientId/users,
 *   /clients/:clientId/pipelines, /clients/:clientId/pipelines/new,
 *   /clients/:clientId/pipelines/:pipelineId,
 *   /clients/:clientId/pipelines/:pipelineId/settings,
 *   /clients/:clientId/pipelines/:pipelineId/documents,
 *   /clients/:clientId/pipelines/:pipelineId/documents/:documentId,
 *   /clients/:clientId/pipelines/:pipelineId/lead-imports,
 *   /clients/:clientId/pipelines/:pipelineId/lead-imports/:batchId,
 *   /clients/:clientId/pipelines/:pipelineId/review,
 *   /clients/:clientId/pipelines/:pipelineId/icp-config,
 *   /clients/:clientId/pipelines/:pipelineId/guardrails,
 *   /clients/:clientId/pipelines/:pipelineId/sources,
 *   /clients/:clientId/pipelines/:pipelineId/policy,
 *   /clients/:clientId/pipelines/:pipelineId/credentials.
 * - / redirects to /clients.
 * - Unknown routes render NotFound.
 * - Each route is wrapped in a RouteErrorBoundary.
 * - No TypeScript `any`.
 */
import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { AppShell } from "../components/layout/AppShell";
import { RouteErrorBoundary } from "../components/feedback/RouteErrorBoundary";
import { ClientListPage } from "../features/clients/ClientListPage";
import { ClientCreatePage } from "../features/clients/ClientCreatePage";
import { ClientDetailPage } from "../features/clients/ClientDetailPage";
import { ClientSettingsPage } from "../features/clients/ClientSettingsPage";
import { ClientUsersPage } from "../features/clients/ClientUsersPage";
import { PipelineListPage } from "../features/clients/PipelineListPage";
import { PipelineCreatePage } from "../features/clients/PipelineCreatePage";
import { PipelineDetailPage } from "../features/clients/PipelineDetailPage";
import { PipelineSettingsPage } from "../features/clients/PipelineSettingsPage";
import { NotFoundPage } from "../features/clients/NotFoundPage";
import { DocumentListPage } from "../features/ingestion/DocumentListPage";
import { DocumentDetailPage } from "../features/ingestion/DocumentDetailPage";
import { LeadImportListPage } from "../features/ingestion/LeadImportListPage";
import { LeadImportDetailPage } from "../features/ingestion/LeadImportDetailPage";
import { ReviewQueuePage } from "../features/review/ReviewQueuePage";
import { ICPConfigPage } from "../features/review/ICPConfigPage";
import { GuardrailsPage } from "../features/review/GuardrailsPage";
import { SourceRegistryPage } from "../features/source/SourceRegistryPage";
import { PolicySimulatorPage } from "../features/source/PolicySimulatorPage";
import { CredentialHealthPage } from "../features/source/CredentialHealthPage";
import CrawlRunMonitorPage from "../features/crawl/CrawlRunMonitorPage";
import ArtifactInspectorPage from "../features/crawl/ArtifactInspectorPage";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<Navigate to="/clients" replace />} />
          <Route
            path="clients"
            element={
              <RouteErrorBoundary>
                <ClientListPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/new"
            element={
              <RouteErrorBoundary>
                <ClientCreatePage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId"
            element={
              <RouteErrorBoundary>
                <ClientDetailPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/settings"
            element={
              <RouteErrorBoundary>
                <ClientSettingsPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/users"
            element={
              <RouteErrorBoundary>
                <ClientUsersPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines"
            element={
              <RouteErrorBoundary>
                <PipelineListPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/new"
            element={
              <RouteErrorBoundary>
                <PipelineCreatePage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId"
            element={
              <RouteErrorBoundary>
                <PipelineDetailPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/settings"
            element={
              <RouteErrorBoundary>
                <PipelineSettingsPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/documents"
            element={
              <RouteErrorBoundary>
                <DocumentListPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/documents/:documentId"
            element={
              <RouteErrorBoundary>
                <DocumentDetailPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/lead-imports"
            element={
              <RouteErrorBoundary>
                <LeadImportListPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/lead-imports/:batchId"
            element={
              <RouteErrorBoundary>
                <LeadImportDetailPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/review"
            element={
              <RouteErrorBoundary>
                <ReviewQueuePage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/icp-config"
            element={
              <RouteErrorBoundary>
                <ICPConfigPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/guardrails"
            element={
              <RouteErrorBoundary>
                <GuardrailsPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/sources"
            element={
              <RouteErrorBoundary>
                <SourceRegistryPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/policy"
            element={
              <RouteErrorBoundary>
                <PolicySimulatorPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/credentials"
            element={
              <RouteErrorBoundary>
                <CredentialHealthPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/crawl"
            element={
              <RouteErrorBoundary>
                <CrawlRunMonitorPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="clients/:clientId/pipelines/:pipelineId/artifacts"
            element={
              <RouteErrorBoundary>
                <ArtifactInspectorPage />
              </RouteErrorBoundary>
            }
          />
          <Route
            path="*"
            element={
              <RouteErrorBoundary>
                <NotFoundPage />
              </RouteErrorBoundary>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
