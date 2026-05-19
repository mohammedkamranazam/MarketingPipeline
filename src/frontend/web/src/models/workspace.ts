/**
 * Acceptance Criteria:
 * - WorkspaceSummary combines client fields needed for navigation and switcher display.
 * - PipelineSummary combines pipeline fields needed for list and switcher display.
 * - No TypeScript `any`.
 */
import type { ClientResponse, PipelineResponse } from "../contracts/clients";

export interface WorkspaceSummary {
  id: string;
  name: string;
  slug: string;
  status: string;
}

export interface PipelineSummary {
  id: string;
  clientId: string;
  name: string;
  slug: string;
  lane: "discovery" | "seed_enrichment";
  status: string;
  description: string | null;
}

export function toWorkspaceSummary(c: ClientResponse): WorkspaceSummary {
  return { id: c.id, name: c.name, slug: c.slug, status: c.status };
}

export function toPipelineSummary(p: PipelineResponse): PipelineSummary {
  return {
    id: p.id,
    clientId: p.client_id,
    name: p.name,
    slug: p.slug,
    lane: p.lane,
    status: p.status,
    description: p.description,
  };
}
