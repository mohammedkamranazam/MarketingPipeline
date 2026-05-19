/**
 * Acceptance Criteria:
 * - listClients() fetches GET /clients and validates response with Zod.
 * - getClient() fetches GET /clients/:id and validates response.
 * - createClient() posts to POST /clients and returns validated ClientResponse.
 * - updateClient() patches PATCH /clients/:id and returns validated ClientResponse.
 * - listPipelines() fetches GET /clients/:id/pipelines.
 * - getPipeline() fetches GET /clients/:id/pipelines/:pid.
 * - createPipeline() posts to POST /clients/:id/pipelines.
 * - updatePipeline() patches PATCH /clients/:id/pipelines/:pid.
 * - No TypeScript `any`.
 */
import {
  ClientListResponseSchema,
  ClientResponseSchema,
  PipelineListResponseSchema,
  PipelineResponseSchema,
  type ClientResponse,
  type CreateClientInput,
  type CreatePipelineInput,
  type PipelineResponse,
  type UpdateClientInput,
  type UpdatePipelineInput,
} from "../contracts/clients";
import { apiFetch } from "./apiClient";

const BASE = "/clients";

export async function listClients(): Promise<ClientResponse[]> {
  const data = await apiFetch<unknown>(BASE);
  return ClientListResponseSchema.parse(data);
}

export async function getClient(id: string): Promise<ClientResponse> {
  const data = await apiFetch<unknown>(`${BASE}/${id}`);
  return ClientResponseSchema.parse(data);
}

export async function createClient(
  input: CreateClientInput,
): Promise<ClientResponse> {
  const data = await apiFetch<unknown>(BASE, {
    method: "POST",
    body: JSON.stringify(input),
  });
  return ClientResponseSchema.parse(data);
}

export async function updateClient(
  id: string,
  input: UpdateClientInput,
): Promise<ClientResponse> {
  const data = await apiFetch<unknown>(`${BASE}/${id}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
  return ClientResponseSchema.parse(data);
}

export async function listPipelines(
  clientId: string,
): Promise<PipelineResponse[]> {
  const data = await apiFetch<unknown>(`${BASE}/${clientId}/pipelines`);
  return PipelineListResponseSchema.parse(data);
}

export async function getPipeline(
  clientId: string,
  pipelineId: string,
): Promise<PipelineResponse> {
  const data = await apiFetch<unknown>(
    `${BASE}/${clientId}/pipelines/${pipelineId}`,
  );
  return PipelineResponseSchema.parse(data);
}

export async function createPipeline(
  clientId: string,
  input: CreatePipelineInput,
): Promise<PipelineResponse> {
  const data = await apiFetch<unknown>(`${BASE}/${clientId}/pipelines`, {
    method: "POST",
    body: JSON.stringify(input),
  });
  return PipelineResponseSchema.parse(data);
}

export async function updatePipeline(
  clientId: string,
  pipelineId: string,
  input: UpdatePipelineInput,
): Promise<PipelineResponse> {
  const data = await apiFetch<unknown>(
    `${BASE}/${clientId}/pipelines/${pipelineId}`,
    {
      method: "PATCH",
      body: JSON.stringify(input),
    },
  );
  return PipelineResponseSchema.parse(data);
}
