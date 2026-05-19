/**
 * Acceptance Criteria:
 * - All client and pipeline API request/response shapes are typed here.
 * - No TypeScript `any` is used.
 * - Zod schemas validate unknown API payloads before use in UI.
 * - ClientResponse, PipelineResponse, CreateClientInput, UpdateClientInput,
 *   CreatePipelineInput, UpdatePipelineInput are all exported.
 */
import { z } from "zod";

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

export const ClientResponseSchema = z.object({
  id: z.string().min(1),
  name: z.string(),
  slug: z.string(),
  status: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const PipelineResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  name: z.string(),
  slug: z.string(),
  lane: z.enum(["discovery", "seed_enrichment"]),
  status: z.string(),
  description: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const ClientListResponseSchema = z.array(ClientResponseSchema);
export const PipelineListResponseSchema = z.array(PipelineResponseSchema);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type ClientResponse = z.infer<typeof ClientResponseSchema>;
export type PipelineResponse = z.infer<typeof PipelineResponseSchema>;

export interface CreateClientInput {
  name: string;
  slug: string;
  status?: string;
}

export interface UpdateClientInput {
  name?: string;
  slug?: string;
  status?: string;
}

export interface CreatePipelineInput {
  name: string;
  slug: string;
  lane: "discovery" | "seed_enrichment";
  description?: string;
}

export interface UpdatePipelineInput {
  name?: string;
  slug?: string;
  lane?: "discovery" | "seed_enrichment";
  status?: string;
  description?: string;
}
