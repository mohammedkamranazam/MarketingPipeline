/**
 * Acceptance Criteria:
 * - Shows loading state while fetching documents.
 * - Shows empty state when pipeline has no documents.
 * - Shows list of documents with filename, status, size, and upload date.
 * - Status badge uses color coding: pending/parsing=warning, parsed/chunked/embedded=success,
 *   failed=error.
 * - Links to document detail page.
 * - Upload button opens file picker and uploads; shows error on failure.
 * - No TypeScript `any`.
 */
import { useRef } from "react";
import { Link, useParams } from "react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listDocuments, uploadDocument } from "../../services/ingestionService";
import type { DocumentResponse } from "../../contracts/ingestion";

function statusBadge(status: string): string {
  if (status === "failed") return "badge-error";
  if (["parsed", "chunked", "embedded"].includes(status)) return "badge-success";
  return "badge-warning";
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function DocumentListPage() {
  const { clientId = "", pipelineId = "" } = useParams();
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);

  const { data: docs, isLoading, error } = useQuery({
    queryKey: ["documents", clientId, pipelineId],
    queryFn: () => listDocuments(clientId, pipelineId),
    enabled: Boolean(clientId && pipelineId),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadDocument(clientId, pipelineId, file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents", clientId, pipelineId] });
    },
  });

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) uploadMutation.mutate(file);
    if (fileRef.current) fileRef.current.value = "";
  }

  const basePath = `/clients/${clientId}/pipelines/${pipelineId}`;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1 text-sm text-base-content/60">
            <Link to={`/clients/${clientId}/pipelines`}>Pipelines</Link>
            <span>/</span>
            <Link to={basePath}>Pipeline</Link>
            <span>/</span>
            <span>Documents</span>
          </div>
          <h1 className="text-xl font-semibold">Documents</h1>
        </div>
        <div>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            onChange={handleFileChange}
            data-testid="file-input"
          />
          <button
            className="btn btn-primary btn-sm"
            onClick={() => fileRef.current?.click()}
            disabled={uploadMutation.isPending}
          >
            {uploadMutation.isPending && (
              <span className="loading loading-spinner loading-xs" />
            )}
            Upload document
          </button>
        </div>
      </div>

      {uploadMutation.isError && (
        <div role="alert" className="alert alert-error mb-4 text-sm">
          {uploadMutation.error instanceof Error
            ? uploadMutation.error.message
            : "Upload failed"}
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center py-12">
          <span className="loading loading-spinner loading-lg" />
        </div>
      )}

      {error && (
        <div role="alert" className="alert alert-error">
          Failed to load documents.
        </div>
      )}

      {!isLoading && !error && docs?.length === 0 && (
        <div className="text-center py-12 text-base-content/50">
          No documents uploaded yet.
        </div>
      )}

      {docs && docs.length > 0 && (
        <div className="overflow-x-auto">
          <table className="table table-zebra w-full">
            <thead>
              <tr>
                <th>File</th>
                <th>Status</th>
                <th>Size</th>
                <th>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc: DocumentResponse) => (
                <tr key={doc.id}>
                  <td>
                    <Link
                      to={`${basePath}/documents/${doc.id}`}
                      className="link link-hover font-mono text-sm"
                    >
                      {doc.original_name}
                    </Link>
                  </td>
                  <td>
                    <span className={`badge ${statusBadge(doc.status)} badge-sm`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="text-sm text-base-content/70">
                    {formatBytes(doc.size_bytes)}
                  </td>
                  <td className="text-sm text-base-content/70">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
