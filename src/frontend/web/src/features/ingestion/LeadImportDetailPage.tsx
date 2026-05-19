/**
 * Acceptance Criteria:
 * - Fetches batch metadata and displays filename, status, total/valid/error rows, dates.
 * - Shows error_message when status is failed.
 * - Fetches and displays seed lead rows in a paginated grid.
 * - Each row shows: row_index, first_name, company, status badge, validation_errors.
 * - Duplicate rows show is_duplicate indicator.
 * - Original vs normalized values are both visible.
 * - Empty rows state shown when batch not yet processed.
 * - No TypeScript `any`.
 */
import { Link, useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { getLeadImport, listSeedLeadRows } from "../../services/ingestionService";
import type { SeedLeadRowResponse } from "../../contracts/ingestion";

function rowStatusBadge(status: string): string {
  if (status === "invalid") return "badge-error";
  if (status === "duplicate") return "badge-warning";
  if (status === "valid") return "badge-success";
  return "badge-ghost";
}

export function LeadImportDetailPage() {
  const { clientId = "", pipelineId = "", batchId = "" } = useParams();

  const { data: batch, isLoading: batchLoading, error: batchError } = useQuery({
    queryKey: ["lead-import", clientId, pipelineId, batchId],
    queryFn: () => getLeadImport(clientId, pipelineId, batchId),
    enabled: Boolean(clientId && pipelineId && batchId),
  });

  const { data: rows, isLoading: rowsLoading } = useQuery({
    queryKey: ["lead-import-rows", clientId, pipelineId, batchId],
    queryFn: () => listSeedLeadRows(clientId, pipelineId, batchId),
    enabled: Boolean(batch),
  });

  const basePath = `/clients/${clientId}/pipelines/${pipelineId}`;

  if (batchLoading) {
    return (
      <div className="flex justify-center py-12">
        <span className="loading loading-spinner loading-lg" />
      </div>
    );
  }

  if (batchError || !batch) {
    return (
      <div role="alert" className="alert alert-error">
        Import batch not found.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4 text-sm text-base-content/60">
        <Link to={`${basePath}/lead-imports`}>Seed lead imports</Link>
        <span>/</span>
        <span className="font-mono">{batch.original_name}</span>
      </div>

      <div className="card bg-base-200 p-4 space-y-3">
        <h1 className="text-lg font-semibold font-mono">{batch.original_name}</h1>
        <div className="flex flex-wrap gap-4 text-sm">
          <span>
            Status:{" "}
            <span
              className={`badge badge-sm ${
                batch.status === "failed" ? "badge-error" : "badge-success"
              }`}
            >
              {batch.status}
            </span>
          </span>
          <span>Total: <strong>{batch.total_rows}</strong></span>
          <span className="text-success">Valid: <strong>{batch.valid_rows}</strong></span>
          <span className="text-error">Errors: <strong>{batch.error_rows}</strong></span>
          <span className="text-base-content/60">
            {new Date(batch.created_at).toLocaleString()}
          </span>
        </div>
        {batch.status === "failed" && batch.error_message && (
          <div role="alert" className="alert alert-error text-sm">
            {batch.error_message}
          </div>
        )}
      </div>

      <section>
        <h2 className="text-base font-semibold mb-3">Rows</h2>
        {rowsLoading && <span className="loading loading-dots loading-sm" />}
        {!rowsLoading && (!rows || rows.length === 0) && (
          <p className="text-sm text-base-content/50">
            No rows available — batch may not have been processed yet.
          </p>
        )}
        {rows && rows.length > 0 && (
          <div className="overflow-x-auto">
            <table className="table table-zebra table-sm w-full">
              <thead>
                <tr>
                  <th>#</th>
                  <th>First name</th>
                  <th>Company</th>
                  <th>Source</th>
                  <th>Status</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row: SeedLeadRowResponse) => (
                  <tr key={row.id}>
                    <td className="text-xs text-base-content/50">{row.row_index + 1}</td>
                    <td>
                      <div className="text-sm">{row.normalized_first_name ?? row.original_first_name ?? "—"}</div>
                      {row.normalized_last_name && (
                        <div className="text-xs text-base-content/50">{row.normalized_last_name}</div>
                      )}
                    </td>
                    <td className="text-sm">
                      {row.normalized_company ?? row.original_company ?? "—"}
                    </td>
                    <td className="text-sm text-base-content/70">
                      {row.normalized_source ?? "—"}
                    </td>
                    <td>
                      <div className="flex flex-col gap-1">
                        <span className={`badge ${rowStatusBadge(row.status)} badge-sm`}>
                          {row.status}
                        </span>
                        {row.is_duplicate && (
                          <span className="badge badge-warning badge-xs">dup</span>
                        )}
                      </div>
                    </td>
                    <td className="text-xs text-base-content/60 max-w-xs truncate">
                      {row.validation_errors.length > 0
                        ? row.validation_errors.join("; ")
                        : row.original_notes ?? ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
