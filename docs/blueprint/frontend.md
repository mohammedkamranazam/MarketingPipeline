# Frontend Roadmap

Acceptance Criteria:
- Define React, TypeScript, Tailwind CSS, and daisyUI as the frontend direction.
- Map the frontend roadmap to the existing blueprint phases without starting later-phase implementation early.
- Cover admin and user perspectives, including required pages, workflows, and navigation.
- List reusable views, components, contracts, models, services, hooks, and test responsibilities.
- Preserve repository rules: no frontend `any`, typed contracts in `src/frontend/web/src/contracts`, models in `src/frontend/web/src/models`, acceptance criteria at the top of code files, and tests for all implemented acceptance criteria.

## Source Alignment

This roadmap extends the modular blueprint. It is a design and implementation plan, not a phase-status change.

- Current project phase: Phase 01, Data Foundation And Workspace API.
- Frontend implementation must follow the backend phase gates in [00-roadmap.md](00-roadmap.md).
- Product workflows and personas come from [03-product-governance.md](03-product-governance.md).
- API groups and event concepts come from [04-data-api-events.md](04-data-api-events.md).
- React/daisyUI setup follows the current daisyUI React installation guide: <https://daisyui.com/docs/install/react/?lang=en>.
- Theme guidance follows daisyUI theme documentation: <https://daisyui.com/docs/themes/?lang=en>.
- Component selection follows the daisyUI component catalog: <https://daisyui.com/components/?lang=en>.

## Product Intent

The frontend is an evidence operations workspace for people who need to turn documents, seed lead lists, permitted sources, provider results, and human decisions into exportable lead intelligence.

Primary humans:

- Admins configuring clients, sources, providers, credentials, guardrails, users, and audits.
- Domain experts approving ICP, title, exclusion, enrichment, suppression, and outreach rules.
- Research reviewers deciding whether evidence-backed leads are accurate enough to approve.
- Sales operators preparing export batches, reviewing outreach readiness, and reading campaign outcomes.
- Compliance reviewers checking source policy, PII lineage, suppression, and audit history.

The interface should feel quiet, dense, inspectable, and accountable. It should behave like an operations console rather than a marketing site. The first screen after login is the app workspace, not a landing page.

## Design Direction

Domain concepts:

- Evidence lineage.
- Source policy.
- Review gates.
- Verified contact data.
- Seed row normalization.
- Citation-backed claims.
- Export eligibility.
- Provider cost and quota.
- Auth recovery.
- Audit trail.

Color world:

- Paper and document whites for readable evidence surfaces.
- Ink and graphite for dense data.
- Teal for verified or policy-approved work.
- Amber for review-needed and policy-warning states.
- Red for blocked, invalid, or suppression-hit states.
- Blue for citations, source links, and inspectable artifacts.
- Muted violet only for intelligence/v2 signals, never as the dominant brand field.

Signature element:

- Evidence Rail: a persistent right-side inspection rail on review, config, source, artifact, lead, and export screens. It shows citations, source policy, reviewer decisions, confidence, lineage, and export blockers for the selected row or entity.

Defaults to avoid:

- Generic metric-card dashboard. Replace with queue-led dashboards that surface work needing action, blockers, and evidence completeness.
- Decorative card-heavy layouts. Replace with dense tables, split panes, timelines, and drawers built for scanning.
- Hidden citations. Replace with citation chips, source snippets, and the Evidence Rail throughout review workflows.
- Free-form admin forms with unclear blast radius. Replace with scoped editors, policy previews, diff views, and confirmation gates.

## Frontend Stack

Use React with Vite, TypeScript, Tailwind CSS 4, and daisyUI 5.

Recommended baseline packages when implementation begins:

```text
react
react-dom
vite
typescript
@vitejs/plugin-react
tailwindcss
@tailwindcss/vite
daisyui
react-router
@tanstack/react-query
@tanstack/react-table
react-hook-form
zod
lucide-react
vitest
@testing-library/react
@testing-library/user-event
msw
playwright
```

The daisyUI React setup should use Tailwind through the Vite plugin and CSS-first daisyUI registration:

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss(), react()],
});
```

```css
/* src/styles/app.css */
@import "tailwindcss";
@plugin "daisyui";
```

Use daisyUI component classes as styling primitives, wrapped by typed project components when behavior, accessibility, or domain meaning is shared. Use Tailwind utilities for layout and small local adjustments. Use `lucide-react` for icons.

## Theme System

Create two custom daisyUI themes:

- `pipeline-light` as the default theme.
- `pipeline-dark` as the preferred dark theme.

Theme goals:

- Radius stays restrained: fields and selectors at `0.25rem`, boxes at `0.5rem`.
- Data surfaces rely on subtle elevation, not heavy borders or shadows.
- Semantic status colors map directly to the product gates.
- Theme switching uses `data-theme` on the document root and persists preference.

Initial theme sketch:

```css
@import "tailwindcss";
@plugin "daisyui" {
  themes: pipeline-light --default, pipeline-dark --prefersdark;
}

@plugin "daisyui/theme" {
  name: "pipeline-light";
  default: true;
  color-scheme: light;
  --color-base-100: oklch(99% 0.004 95);
  --color-base-200: oklch(96% 0.006 95);
  --color-base-300: oklch(91% 0.009 95);
  --color-base-content: oklch(22% 0.02 250);
  --color-primary: oklch(46% 0.095 180);
  --color-primary-content: oklch(98% 0.01 180);
  --color-secondary: oklch(47% 0.08 255);
  --color-secondary-content: oklch(98% 0.01 255);
  --color-accent: oklch(72% 0.15 78);
  --color-accent-content: oklch(20% 0.03 78);
  --color-neutral: oklch(30% 0.018 250);
  --color-neutral-content: oklch(98% 0.005 250);
  --color-info: oklch(58% 0.12 240);
  --color-info-content: oklch(98% 0.01 240);
  --color-success: oklch(58% 0.12 155);
  --color-success-content: oklch(98% 0.01 155);
  --color-warning: oklch(76% 0.15 78);
  --color-warning-content: oklch(22% 0.04 78);
  --color-error: oklch(57% 0.18 28);
  --color-error-content: oklch(98% 0.01 28);
  --radius-selector: 0.25rem;
  --radius-field: 0.25rem;
  --radius-box: 0.5rem;
  --size-selector: 0.25rem;
  --size-field: 0.25rem;
  --border: 1px;
  --depth: 1;
  --noise: 0;
}

@plugin "daisyui/theme" {
  name: "pipeline-dark";
  prefersdark: true;
  color-scheme: dark;
  --color-base-100: oklch(17% 0.015 250);
  --color-base-200: oklch(21% 0.016 250);
  --color-base-300: oklch(27% 0.018 250);
  --color-base-content: oklch(93% 0.008 95);
  --color-primary: oklch(68% 0.095 180);
  --color-primary-content: oklch(15% 0.018 180);
  --color-secondary: oklch(70% 0.075 255);
  --color-secondary-content: oklch(16% 0.02 255);
  --color-accent: oklch(78% 0.13 78);
  --color-accent-content: oklch(18% 0.03 78);
  --color-neutral: oklch(88% 0.006 250);
  --color-neutral-content: oklch(18% 0.016 250);
  --color-info: oklch(72% 0.105 240);
  --color-info-content: oklch(15% 0.02 240);
  --color-success: oklch(72% 0.11 155);
  --color-success-content: oklch(15% 0.02 155);
  --color-warning: oklch(80% 0.13 78);
  --color-warning-content: oklch(17% 0.03 78);
  --color-error: oklch(68% 0.15 28);
  --color-error-content: oklch(98% 0.01 28);
  --radius-selector: 0.25rem;
  --radius-field: 0.25rem;
  --radius-box: 0.5rem;
  --size-selector: 0.25rem;
  --size-field: 0.25rem;
  --border: 1px;
  --depth: 1;
  --noise: 0;
}
```

Add app-specific semantic CSS variables on top of daisyUI only when daisyUI's semantic colors are too broad:

```css
:root {
  --signal-evidence: var(--color-info);
  --signal-policy: var(--color-warning);
  --signal-verified: var(--color-success);
  --signal-blocked: var(--color-error);
}
```

## Frontend Architecture

Target layout:

```text
src/frontend/web/
  src/
    app/
      App.tsx
      router.tsx
      providers/
      styles/
    assets/
    components/
      primitives/
      layout/
      data-display/
      forms/
      workflow/
      evidence/
      charts/
      feedback/
    contracts/
    features/
      auth/
      clients/
      documents/
      lead-imports/
      knowledge/
      review/
      sources/
      providers/
      runs/
      artifacts/
      enrichment/
      leads/
      exports/
      feedback/
      admin/
      intelligence/
      integrations/
    hooks/
    models/
    routes/
    services/
    test/
    utils/
```

Rules:

- Long-lived DTOs live in `contracts`.
- UI/domain models live in `models`.
- API calls live in `services`.
- Feature folders compose views from shared components and typed services.
- Components do not import backend implementation code.
- Components do not use TypeScript `any`.
- Code files start with acceptance criteria comments before implementation.
- Unit tests cover acceptance criteria and important edge cases.

## Application Shell

The shell must support multi-tenant operations and fast review work.

Required shell components:

- `AppProviders`: query client, router, theme, auth, toast, feature flags.
- `AppShell`: desktop sidebar, mobile drawer, topbar, content region, optional Evidence Rail.
- `SidebarNav`: phase-aware navigation grouped by Work, Config, Operations, Admin.
- `Topbar`: workspace switcher, global search, notifications, theme controller, user menu.
- `WorkspaceSwitcher`: selected client, role visibility, quick client switch.
- `CommandPalette`: jump to client, import, review item, source, lead, export batch.
- `EvidenceRail`: selected entity evidence, citations, policy, lineage, blockers, audit.
- `PageHeader`: title, status, breadcrumbs, primary action, secondary actions.
- `FilterBar`: saved filters, chips, search, date range, owner, status.
- `ToastHost`: mutation success/failure and background job status.
- `RouteErrorBoundary`: route-scoped failure state with retry and support details.

## Navigation Model

Primary user navigation inside a client workspace:

- Overview.
- Ingestion.
- Knowledge and ICP.
- Sources and Providers.
- Runs and Artifacts.
- Enrichment.
- Review.
- Exports.
- Feedback.

Admin navigation:

- Clients.
- Users and Roles.
- Sources and Providers.
- Credentials.
- Auth Sessions.
- Jobs and Runs.
- Audit.
- Feature Flags.
- Integrations.
- System Settings.

Mobile behavior:

- Use daisyUI `drawer` for navigation.
- Keep the Evidence Rail as a full-screen drawer on small viewports.
- Keep tables readable through column presets, row detail drawers, and horizontal scroll only when unavoidable.

## Global Pages

These pages sit outside a single phase-specific workspace route but are required for a complete app shell.

| Route | Personas | Purpose |
|---|---|---|
| `/login` | All | Authenticate and route the user to the last selected workspace. |
| `/logout` | All | Clear local session state and redirect to login. |
| `/workspaces` | All | Select or request access to a client workspace. |
| `/profile` | All | Manage user name, notification preferences, theme, and keyboard settings. |
| `/notifications` | All | Review job, auth, export, and review-task notifications. |
| `/403` | All | Explain missing role or workspace access. |
| `/404` | All | Recover from unknown routes with workspace-aware navigation. |
| `/system/status` | Admin | Inspect frontend build, API health, and environment metadata. |

## Page Inventory By Phase

| Phase | Routes | Primary personas | Purpose |
|---|---|---|---|
| 00 | `/health`, `/system/status` | Admin | Show frontend/API reachability and environment status. |
| 01 | `/clients`, `/clients/new`, `/clients/:clientId`, `/clients/:clientId/settings`, `/clients/:clientId/users` | Admin | Create, list, inspect, and update client workspaces and settings. |
| 02 | `/clients/:clientId/documents`, `/clients/:clientId/documents/:documentId`, `/clients/:clientId/lead-imports`, `/clients/:clientId/lead-imports/:batchId`, `/clients/:clientId/knowledge` | Admin, domain expert, research reviewer | Upload documents and seed lead sheets, inspect parse status, extracted knowledge, validation errors, and citations. |
| 03 | `/clients/:clientId/review/config`, `/clients/:clientId/config/icp`, `/clients/:clientId/config/guardrails`, `/clients/:clientId/config/suppression`, `/clients/:clientId/config/title-mappings` | Domain expert, compliance reviewer | Approve ICP suggestions and activate enrichment, verification, suppression, and outreach guardrails. |
| 04 | `/clients/:clientId/sources`, `/clients/:clientId/sources/:sourceId`, `/clients/:clientId/providers`, `/clients/:clientId/policies`, `/clients/:clientId/credentials` | Admin, compliance reviewer | Configure sources, providers, operation policy, credentials, rate limits, and policy previews. |
| 05 | `/clients/:clientId/runs/crawl`, `/clients/:clientId/artifacts`, `/clients/:clientId/artifacts/:artifactId`, `/clients/:clientId/runs/search` | Admin, research reviewer | Monitor crawl/search jobs, inspect artifacts, failures, costs, and lineage. |
| 06 | `/clients/:clientId/extractions`, `/clients/:clientId/profile-candidates`, `/clients/:clientId/email-verifications`, `/clients/:clientId/enrichment` | Research reviewer, sales operator | Inspect extracted companies, signals, contacts, profile candidates, provider results, verification outcomes, and evidence. |
| 07 | `/clients/:clientId/leads`, `/clients/:clientId/leads/:leadId`, `/clients/:clientId/review/leads`, `/clients/:clientId/exports`, `/clients/:clientId/exports/:exportId`, `/clients/:clientId/outreach-exports` | Research reviewer, sales operator, compliance reviewer | Review, approve, reject, edit, score, simulate compliance, and export approved leads. |
| 08 | `/clients/:clientId/auth-sessions`, `/clients/:clientId/auth-sessions/:sessionId`, `/clients/:clientId/auth-recovery` | Admin, compliance reviewer | Validate authenticated sources, resolve MFA/CAPTCHA challenges, refresh sessions, and resume paused jobs. |
| 09 | `/admin/runs`, `/admin/audit`, `/admin/metrics`, `/admin/llm-invocations`, `/admin/export-simulation`, `/admin/feature-flags` | Admin, compliance reviewer | Operate production jobs, audit actions, inspect costs, and monitor SLOs. |
| 10 | `/clients/:clientId/intelligence/hypotheses`, `/clients/:clientId/intelligence/signals`, `/clients/:clientId/intelligence/attention`, `/clients/:clientId/strategy` | Admin, domain expert, sales operator | Prioritize work by expected value, temporal signals, skeptic pass, and campaign strategy. |
| 11 | `/clients/:clientId/integrations/crm`, `/clients/:clientId/integrations/outreach`, `/clients/:clientId/outcomes`, `/admin/enterprise`, `/admin/provider-quality` | Admin, sales operator | Manage CRM/outreach mappings, outcome ingestion, provider quality, tenant scale, and enterprise governance. |

## Admin Perspective

Admin workflows:

- Create a client workspace and configure default discovery/enrichment/export settings.
- Invite users and assign roles.
- Configure source connectors, providers, credentials, and operation scopes.
- Preview policy decisions before enabling a source or provider.
- Monitor runs, auth sessions, provider quotas, costs, and production metrics.
- Review audit logs and before/after configuration diffs.
- Manage feature flags for later intelligence and enterprise capabilities.

Admin pages:

- Client list.
- Client create/edit.
- Client settings.
- User and role management.
- Source registry.
- Provider registry.
- Credential vault metadata.
- Policy simulator.
- Auth sessions and recovery queue.
- Run monitor.
- Metrics dashboard.
- Audit log.
- Feature flags.
- CRM/outreach integration settings.
- Enterprise tenant dashboard.

Admin-specific components:

- `ClientWorkspaceForm`.
- `ClientSettingsEditor`.
- `RoleAssignmentTable`.
- `SourceConnectorForm`.
- `ProviderConnectorForm`.
- `CredentialScopePicker`.
- `PolicySimulator`.
- `PolicyDecisionBadge`.
- `RateLimitEditor`.
- `QuotaUsagePanel`.
- `AuthSessionCard`.
- `AuditLogTable`.
- `AuditDiffViewer`.
- `FeatureFlagToggle`.
- `IntegrationMappingEditor`.

## User Perspective

Operational user workflows:

- Upload client documents and seed lead lists.
- Inspect parse, row validation, and extraction outcomes.
- Approve or edit suggested ICP and guardrails.
- Review source artifacts, profile matches, provider enrichment, email verification, and lead scores.
- Approve, reject, edit, or route leads to manual follow-up.
- Build CRM-ready and outreach-ready export batches.
- Inspect feedback outcomes and adjust future review priorities.

User pages:

- Workspace overview.
- Document ingestion.
- Document detail and citation viewer.
- Seed lead import list.
- Seed lead batch detail and row validation.
- Knowledge suggestions.
- ICP review.
- Guardrail review.
- Crawl/search monitor.
- Artifact inspector.
- Enrichment monitor.
- Profile candidate comparison.
- Lead review queue.
- Lead detail.
- Export batch builder.
- Feedback dashboard.
- User profile and preferences.

User-specific components:

- `UploadDropzone`.
- `DocumentStatusTimeline`.
- `CitationSnippet`.
- `SeedLeadImportWizard`.
- `SeedLeadRowGrid`.
- `RowValidationBadge`.
- `SuggestionReviewCard`.
- `IcpRuleEditor`.
- `GuardrailChecklist`.
- `ArtifactPreview`.
- `ProfileCandidateCompare`.
- `EmailVerificationBadge`.
- `LeadScoreBreakdown`.
- `LeadDecisionToolbar`.
- `ManualFollowUpQueue`.
- `ExportWizard`.
- `FeedbackOutcomeFunnel`.

## Reusable Views

Reusable views are route-level composition patterns used across features.

- `EntityListView`: table, filters, saved views, bulk action bar, empty state, pagination.
- `EntityDetailView`: header, metadata, status timeline, tabs, Evidence Rail.
- `ReviewWorkspaceView`: queue list, selected item detail, evidence rail, decision toolbar.
- `ConfigEditorView`: form sections, policy preview, before/after diff, save confirmation.
- `RunMonitorView`: stats strip, timeline, error table, retry controls, cost/quota panel.
- `ArtifactInspectorView`: source metadata, raw/parsed tabs, citation anchors, lineage.
- `ExportWizardView`: eligible rows, blockers, compliance simulation, field mapping, download.
- `MetricsDashboardView`: SLO cards, trends, error slices, queue age, provider metrics.
- `SettingsView`: fieldsets, scoped forms, dirty-state guard, audit note prompt.

## Reusable Component Inventory

Primitive wrappers around daisyUI:

- `Button`, `IconButton`, `ButtonGroup`.
- `DropdownMenu`.
- `Modal`, `ConfirmDialog`.
- `Drawer`.
- `Tabs`.
- `Badge`, `StatusDot`.
- `Alert`.
- `Toast`.
- `Tooltip`.
- `ProgressBar`, `RadialProgress`.
- `SkeletonBlock`.
- `TableShell`.
- `Pagination`.
- `Breadcrumbs`.
- `MenuList`.
- `StatBlock`.
- `Timeline`.
- `Steps`.
- `Accordion`, `CollapsePanel`.
- `Fieldset`, `FormField`, `Label`.
- `TextInput`, `Textarea`, `Select`, `Checkbox`, `RadioGroup`, `Toggle`, `Range`.
- `FileInput`.
- `EmptyState`.
- `ErrorState`.

Layout components:

- `AppShell`.
- `SidebarNav`.
- `Topbar`.
- `WorkspaceSwitcher`.
- `CommandPalette`.
- `EvidenceRail`.
- `SplitPane`.
- `DetailDrawer`.
- `PageHeader`.
- `PageSection`.
- `FilterBar`.
- `BulkActionBar`.
- `MobileBottomDock`.

Data and evidence components:

- `CitationChip`.
- `CitationList`.
- `CitationSnippet`.
- `SourceLink`.
- `LineageTimeline`.
- `PolicyDecisionPanel`.
- `ConfidenceMeter`.
- `ScoreBreakdown`.
- `DiffViewer`.
- `AuditActorStamp`.
- `CostBadge`.
- `QuotaMeter`.
- `RetryClassBadge`.
- `ExportEligibilityBadge`.

Workflow components:

- `JobStatusTimeline`.
- `ReviewQueue`.
- `ReviewDecisionToolbar`.
- `ManualFollowUpPanel`.
- `ApprovalGate`.
- `ComplianceGate`.
- `PolicyPreview`.
- `SuppressionHitPanel`.
- `CredentialHealthPanel`.
- `AuthChallengePanel`.
- `WizardShell`.

Domain components:

- `ClientWorkspaceCard`.
- `ClientSettingsEditor`.
- `DocumentUploadPanel`.
- `DocumentParseTimeline`.
- `SeedLeadImportWizard`.
- `SeedLeadRowGrid`.
- `KnowledgeSuggestionList`.
- `IcpEditor`.
- `TitleMappingEditor`.
- `SuppressionListEditor`.
- `GuardrailEditor`.
- `SourceConnectorCard`.
- `SourceConnectorForm`.
- `ProviderConnectorCard`.
- `ProviderConnectorForm`.
- `CrawlJobTable`.
- `ArtifactPreview`.
- `ExtractionEntityTable`.
- `ProfileCandidateCompare`.
- `EmailVerificationPanel`.
- `LeadCard`.
- `LeadDetailHeader`.
- `LeadScoreBreakdown`.
- `ExportBatchBuilder`.
- `OutreachPayloadPreview`.
- `FeedbackFunnel`.
- `HypothesisBoard`.
- `StrategyModeSelector`.
- `IntegrationMappingEditor`.

## Service Inventory

All services return typed contracts and should be tested with MSW fixtures.

Core services:

- `apiClient`: base URL, auth headers, typed errors, request IDs.
- `authService`: login/session/current user hooks when auth exists.
- `themeService`: theme preference and system preference resolution.
- `featureFlagService`: flag reads and route guards.
- `notificationService`: toast and background job notifications.

Workspace services:

- `clientService`: `/clients`.
- `clientUserService`: client users and roles.
- `clientSettingsService`: workspace settings, modes, export defaults, guardrails.

Ingestion services:

- `documentService`: `/documents`.
- `documentUploadService`: upload, retry, parse status.
- `leadImportService`: `/lead-imports`.
- `knowledgeService`: `/knowledge`.

Config and policy services:

- `icpConfigService`: `/config/icp`.
- `reviewService`: `/review`.
- `sourceService`: `/sources`.
- `sourcePolicyService`: `/source-policies`.
- `credentialService`: `/credentials`.
- `providerService`: `/enrichment-providers`.

Operations services:

- `crawlJobService`: `/crawl-jobs`.
- `artifactService`: `/artifacts`.
- `extractionService`: `/extractions`.
- `profileCandidateService`: `/profile-candidates`.
- `emailVerificationService`: `/email-verifications`.
- `adminRunService`: `/admin/runs`.
- `authSessionService`: `/auth-sessions`.

Lead and export services:

- `leadService`: `/leads`.
- `exportService`: `/exports`.
- `outreachExportService`: `/outreach-exports`.
- `feedbackService`: `/feedback`.

Production and enterprise services:

- `auditService`: audit logs.
- `metricsService`: SLO and provider metrics.
- `llmInvocationService`: LLM cost/token traces.
- `integrationService`: CRM/outreach mappings.
- `outcomeService`: outcome ingestion and engagement events.
- `intelligenceService`: hypotheses, signals, attention, strategy mode.

## Hook Inventory

Shared hooks must stay typed and focused on UI orchestration, not business rules.

- `useCurrentUser`.
- `useWorkspace`.
- `useWorkspaceRequiredRoute`.
- `useRoleGate`.
- `useThemePreference`.
- `useFeatureFlag`.
- `useDebouncedValue`.
- `useUrlTableState`.
- `useSavedView`.
- `useBulkSelection`.
- `useConfirmDialog`.
- `useToast`.
- `useEvidenceRail`.
- `useReviewKeyboardShortcuts`.
- `useDirtyFormGuard`.
- `usePollingJobStatus`.
- `useExportEligibility`.
- `usePolicyPreview`.
- `useAuthRecovery`.

## Contracts And Models

Frontend contracts mirror API request/response DTOs and live in `src/frontend/web/src/contracts`.

Required contract groups:

- `health`.
- `clients`.
- `client-users`.
- `client-settings`.
- `documents`.
- `lead-imports`.
- `knowledge`.
- `review`.
- `icp-config`.
- `sources`.
- `source-policies`.
- `credentials`.
- `crawl-jobs`.
- `artifacts`.
- `extractions`.
- `profile-candidates`.
- `enrichment-providers`.
- `email-verifications`.
- `leads`.
- `exports`.
- `outreach-exports`.
- `feedback`.
- `auth-sessions`.
- `admin-runs`.
- `audit`.
- `metrics`.
- `integrations`.
- `intelligence`.

UI models live in `src/frontend/web/src/models` and may combine multiple contracts for rendering. Examples:

- `WorkspaceSummary`.
- `ReviewQueueItem`.
- `EvidenceReference`.
- `PolicyGateState`.
- `ImportRowViewModel`.
- `ArtifactViewModel`.
- `ProfileCandidateViewModel`.
- `LeadReviewViewModel`.
- `ExportEligibilityViewModel`.
- `MetricTileModel`.

Use schema validation for unknown API payloads before they cross into UI models.

## State Management

- Use TanStack Query for server state, caching, invalidation, retries, and optimistic review/export mutations.
- Use URL search params for table filters, selected saved view, sort, and pagination.
- Use local React state for open/closed UI controls.
- Use reducers for complex page-local workflow state such as import mapping, export wizard, and review keyboard flow.
- Use React context only for app-wide stable concerns: auth, theme, feature flags, and workspace selection.
- Use Suspense and route error boundaries only when data-loading behavior is predictable and tested.

## Forms And Validation

- Use React Hook Form for complex forms and Zod for typed validation.
- Keep form schemas near contracts when they represent API input.
- Show policy previews before saving risky source, credential, guardrail, or export changes.
- Preserve dirty-state warnings for long forms.
- Never submit raw unvalidated form data across service boundaries.
- Server validation errors map to field errors and page-level alerts.

## Tables And Queues

Use TanStack Table for dense operational tables:

- Column visibility presets per page.
- Row selection and bulk actions.
- Server-side pagination, sorting, and filtering.
- Keyboard navigation for review queues.
- Row detail drawers for evidence and audit details.
- CSV/XLSX export only through backend export APIs, never by scraping UI state.

Required dense tables:

- Clients.
- Users and roles.
- Documents.
- Seed import rows.
- Review items.
- Sources.
- Providers.
- Credentials.
- Policy decisions.
- Crawl/search jobs.
- Artifacts.
- Extractions.
- Profile candidates.
- Email verifications.
- Leads.
- Export batch items.
- Audit logs.
- Metrics details.

## Accessibility And Interaction

- Every icon-only button has an accessible label and tooltip.
- Every modal/drawer traps focus and returns focus on close.
- Every table action has keyboard access.
- Form errors are tied to fields.
- Loading states use skeletons for content areas and daisyUI loading indicators for actions.
- Status is communicated with text plus color, not color alone.
- Review decisions support keyboard shortcuts after explicit user enablement.
- Reduced-motion preference is respected for transitions.

## Testing Roadmap

Frontend implementation tests must include:

- Unit tests for utilities, model mappers, reducers, and services.
- Component tests for every shared component with acceptance criteria.
- MSW-backed service and feature tests for success, validation failure, auth failure, and server error states.
- Accessibility checks for dialogs, drawers, forms, and review actions.
- Playwright smoke tests for phase-level user journeys once pages exist.

Phase-level frontend smoke tests:

- Phase 01: create/list/update client workspace.
- Phase 02: upload document and seed lead file, inspect parser or validation result.
- Phase 03: approve/edit/reject ICP suggestion and guardrail.
- Phase 04: create source/provider and preview policy.
- Phase 05: inspect crawl/search job and artifact.
- Phase 06: inspect profile candidates and email verification states.
- Phase 07: approve lead and create compliant export batch.
- Phase 08: refresh auth session and resume paused job.
- Phase 09: filter audit log and inspect metrics.
- Phase 10: sort attention queue by intelligence score behind feature flag.
- Phase 11: configure CRM/outreach mapping and inspect outcomes.

## Frontend Definition Of Done

For every implemented frontend ticket:

- Acceptance criteria are at the top of new or changed code files.
- Contracts/models are typed and stored in the correct folders.
- No frontend TypeScript `any` is introduced.
- Loading, empty, error, and permission states are implemented.
- Forms validate before submit and display server errors.
- Evidence, policy, and audit context are visible where decisions are made.
- Unit/component tests cover acceptance criteria and important edge cases.
- Playwright smoke coverage exists for user-facing phase workflows when practical.
- `make -f devops/Makefile test` and `make -f devops/Makefile lint` pass before marking work done.
