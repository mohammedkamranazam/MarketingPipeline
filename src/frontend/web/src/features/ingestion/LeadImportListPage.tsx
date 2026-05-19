/**
 * Acceptance Criteria:
 * - Shows loading state while fetching lead import batches.
 * - Shows empty state when no batches exist.
 * - Shows list of batches with filename, status, row counts, and upload date.
 * - Upload button accepts CSV or XLSX files; shows error on failure.
 * - Links to batch detail page.
 * - Status badge uses color coding.
 * - No TypeScript `any`.
 */
import { useRef } from "react";
import { Link, useParams } from "react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listLeadImports, uploadLeadImport } from "../../services/ingestionService";
import type { LeadImportBatchResponse } from "../../contracts/ingestion";

function statusBadge(status: string): string {
  if (status === "failed") return "badge-error";
  if (status === "completed") return "badge-success";
  if (status === "processing") return "badge-warning";
  return "badge-ghost";
}

export function LeadImportListPage() {
  const { clientId = "", pipelineId = "" } = useParams();
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);

  const { data: batches, isLoading, error } = useQuery({
    queryKey: ["lead-imports", clientId, pipelineId],
    queryFn: () => listLeadImports(clientId, pipelineId),
    enabled: Boolean(clientId && pipelineId),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadLeadImport(clientId, pipelineId, file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["lead-imports", clientId, pipelineId] });
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
            <span>Seed Leads</span>
          </div>
          <h1 className="text-xl font-semibold">Seed lead imports</h1>
        </div>
        <div>
          <input
            ref={fileRef}
            type="file"
            accept=".csv,.xlsx"
            className="hidden"
            onChange={handleFileChange}
            data-testid="lead-file-input"
          />
          <button
            className="btn btn-primary btn-sm"
            onClick={() => fileRef.current?.click()}
            disabled={uploadMutation.isPending}
          >
            {uploadMutation.isPending && (
              <span className="loading loading-spinner loading-xs" />
            )}
            Upload CSV / XLSX
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
          Failed to load imports.
        </div>
      )}

      {!isLoading && !error && batches?.length === 0 && (
        <div className="text-center py-12 text-base-content/50">
          No seed lead files uploaded yet.
        </div>
      )}

      {batches && batches.length > 0 && (
        <div className="overflow-x-auto">
          <table className="table table-zebra w-full">
            <thead>
              <tr>
                <th>File</th>
                <th>Status</th>
                <th>Rows</th>
                <th>Valid</th>
                <th>Errors</th>
                <th>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {batches.map((batch: LeadImportBatchResponse) => (
                <tr key={batch.id}>
                  <td>
                    <Link
                      to={`${basePath}/lead-imports/${batch.id}`}
                      className="link link-hover font-mono text-sm"
                    >
                      {batch.original_name}
                    </Link>
                  </td>
                  <td>
                    <span className={`badge ${statusBadge(batch.status)} badge-sm`}>
                      {batch.status}
                    </span>
                  </td>
                  <td className="text-sm">{batch.total_rows}</td>
                  <td className="text-sm text-success">{batch.valid_rows}</td>
                  <td className="text-sm text-error">{batch.error_rows}</td>
                  <td className="text-sm text-base-content/70">
                    {new Date(batch.created_at).toLocaleDateString()}
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
