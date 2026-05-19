/**
 * Acceptance Criteria:
 * - listDocuments(clientId, pipelineId) fetches GET /clients/:cid/pipelines/:pid/documents.
 * - getDocument(clientId, pipelineId, documentId) fetches the single document.
 * - uploadDocument(clientId, pipelineId, file) posts multipart form data and returns
 *   DocumentResponse.
 * - listKnowledgeItems(clientId, pipelineId, documentId) fetches knowledge items.
 * - listLeadImports(clientId, pipelineId) fetches lead import batches.
 * - getLeadImport(clientId, pipelineId, batchId) fetches a single batch.
 * - uploadLeadImport(clientId, pipelineId, file) posts multipart form data and returns
 *   LeadImportBatchResponse.
 * - listSeedLeadRows(clientId, pipelineId, batchId) fetches seed lead rows for the batch.
 * - All responses validated with Zod schemas.
 * - No TypeScript `any`.
 */
import {
  DocumentListResponseSchema,
  DocumentResponseSchema,
  KnowledgeItemListResponseSchema,
  LeadImportBatchListResponseSchema,
  LeadImportBatchResponseSchema,
  SeedLeadRowListResponseSchema,
  type DocumentResponse,
  type ExtractedKnowledgeItemResponse,
  type LeadImportBatchResponse,
  type SeedLeadRowResponse,
} from "../contracts/ingestion";
import { API_BASE } from "./apiClient";
import { apiFetch } from "./apiClient";

function docBase(clientId: string, pipelineId: string): string {
  return `/clients/${clientId}/pipelines/${pipelineId}/documents`;
}

function importBase(clientId: string, pipelineId: string): string {
  return `/clients/${clientId}/pipelines/${pipelineId}/lead-imports`;
}

export async function listDocuments(
  clientId: string,
  pipelineId: string,
): Promise<DocumentResponse[]> {
  const data = await apiFetch<unknown>(docBase(clientId, pipelineId));
  return DocumentListResponseSchema.parse(data);
}

export async function getDocument(
  clientId: string,
  pipelineId: string,
  documentId: string,
): Promise<DocumentResponse> {
  const data = await apiFetch<unknown>(`${docBase(clientId, pipelineId)}/${documentId}`);
  return DocumentResponseSchema.parse(data);
}

export async function uploadDocument(
  clientId: string,
  pipelineId: string,
  file: File,
): Promise<DocumentResponse> {
  const form = new FormData();
  form.append("file", file);
  const url = `${API_BASE}${docBase(clientId, pipelineId)}`;
  const res = await fetch(url, { method: "POST", body: form });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // use default
    }
    throw new Error(detail);
  }
  return DocumentResponseSchema.parse(await res.json());
}

export async function listKnowledgeItems(
  clientId: string,
  pipelineId: string,
  documentId: string,
): Promise<ExtractedKnowledgeItemResponse[]> {
  const data = await apiFetch<unknown>(
    `${docBase(clientId, pipelineId)}/${documentId}/knowledge`,
  );
  return KnowledgeItemListResponseSchema.parse(data);
}

export async function listLeadImports(
  clientId: string,
  pipelineId: string,
): Promise<LeadImportBatchResponse[]> {
  const data = await apiFetch<unknown>(importBase(clientId, pipelineId));
  return LeadImportBatchListResponseSchema.parse(data);
}

export async function getLeadImport(
  clientId: string,
  pipelineId: string,
  batchId: string,
): Promise<LeadImportBatchResponse> {
  const data = await apiFetch<unknown>(`${importBase(clientId, pipelineId)}/${batchId}`);
  return LeadImportBatchResponseSchema.parse(data);
}

export async function uploadLeadImport(
  clientId: string,
  pipelineId: string,
  file: File,
): Promise<LeadImportBatchResponse> {
  const form = new FormData();
  form.append("file", file);
  const url = `${API_BASE}${importBase(clientId, pipelineId)}`;
  const res = await fetch(url, { method: "POST", body: form });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // use default
    }
    throw new Error(detail);
  }
  return LeadImportBatchResponseSchema.parse(await res.json());
}

export async function listSeedLeadRows(
  clientId: string,
  pipelineId: string,
  batchId: string,
): Promise<SeedLeadRowResponse[]> {
  const data = await apiFetch<unknown>(
    `${importBase(clientId, pipelineId)}/${batchId}/rows`,
  );
  return SeedLeadRowListResponseSchema.parse(data);
}
