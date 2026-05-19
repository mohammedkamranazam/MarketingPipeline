/**
 * Acceptance Criteria:
 * - Fetches document metadata and displays filename, status, mime_type, size, dates.
 * - Shows error_message when status is failed.
 * - Fetches and displays extracted knowledge items with evidence and confidence.
 * - Shows empty state when no knowledge items exist.
 * - Loading skeleton while data is loading.
 * - 404 case shows not found message.
 * - No TypeScript `any`.
 */
import { Link, useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { getDocument, listKnowledgeItems } from "../../services/ingestionService";
import type { ExtractedKnowledgeItemResponse } from "../../contracts/ingestion";

function confidenceColor(c: number): string {
  if (c >= 0.8) return "text-success";
  if (c >= 0.5) return "text-warning";
  return "text-error";
}

export function DocumentDetailPage() {
  const { clientId = "", pipelineId = "", documentId = "" } = useParams();

  const { data: doc, isLoading: docLoading, error: docError } = useQuery({
    queryKey: ["document", clientId, pipelineId, documentId],
    queryFn: () => getDocument(clientId, pipelineId, documentId),
    enabled: Boolean(clientId && pipelineId && documentId),
  });

  const { data: items, isLoading: itemsLoading } = useQuery({
    queryKey: ["knowledge", clientId, pipelineId, documentId],
    queryFn: () => listKnowledgeItems(clientId, pipelineId, documentId),
    enabled: Boolean(doc),
  });

  const basePath = `/clients/${clientId}/pipelines/${pipelineId}`;

  if (docLoading) {
    return (
      <div className="flex justify-center py-12">
        <span className="loading loading-spinner loading-lg" />
      </div>
    );
  }

  if (docError || !doc) {
    return (
      <div role="alert" className="alert alert-error">
        Document not found.
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center gap-2 mb-4 text-sm text-base-content/60">
        <Link to={`${basePath}/documents`}>Documents</Link>
        <span>/</span>
        <span className="font-mono">{doc.original_name}</span>
      </div>

      <div className="card bg-base-200 p-4 space-y-2">
        <h1 className="text-lg font-semibold font-mono">{doc.original_name}</h1>
        <div className="flex gap-4 text-sm flex-wrap">
          <span>
            Status:{" "}
            <span
              className={`badge badge-sm ${
                doc.status === "failed" ? "badge-error" : "badge-success"
              }`}
            >
              {doc.status}
            </span>
          </span>
          <span className="text-base-content/60">{doc.mime_type}</span>
          <span className="text-base-content/60">{doc.size_bytes.toLocaleString()} bytes</span>
          <span className="text-base-content/60">
            Uploaded {new Date(doc.created_at).toLocaleString()}
          </span>
        </div>
        {doc.status === "failed" && doc.error_message && (
          <div role="alert" className="alert alert-error text-sm mt-2">
            {doc.error_message}
          </div>
        )}
      </div>

      <section>
        <h2 className="text-base font-semibold mb-3">Extracted knowledge</h2>
        {itemsLoading && <span className="loading loading-dots loading-sm" />}
        {!itemsLoading && (!items || items.length === 0) && (
          <p className="text-sm text-base-content/50">
            No knowledge items extracted yet.
          </p>
        )}
        {items && items.length > 0 && (
          <ul className="space-y-3">
            {items.map((item: ExtractedKnowledgeItemResponse) => (
              <li key={item.id} className="card bg-base-200 p-3 text-sm">
                <div className="flex gap-2 items-start justify-between">
                  <span className="badge badge-ghost badge-sm">{item.item_type}</span>
                  <span className={`font-mono text-xs ${confidenceColor(item.confidence)}`}>
                    {(item.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <p className="mt-1 font-medium">{item.content}</p>
                <blockquote className="mt-1 pl-2 border-l-2 border-base-content/20 text-base-content/60 italic text-xs">
                  {item.evidence_text}
                  {item.evidence_page !== null && (
                    <span className="ml-2 not-italic">p.{item.evidence_page}</span>
                  )}
                </blockquote>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
