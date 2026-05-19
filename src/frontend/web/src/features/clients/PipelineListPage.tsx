/**
 * Acceptance Criteria:
 * - Shows pipeline list for the current client.
 * - Shows loading skeleton, empty state, populated table, and error state.
 * - Shows pipeline name, lane badge, status badge, and link to detail.
 * - Link to create a new pipeline.
 * - No TypeScript `any`.
 */
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { Plus } from "lucide-react";
import { listPipelines, getClient } from "../../services/clientService";
import { ApiError } from "../../services/apiClient";

const LANE_LABEL: Record<string, string> = {
  discovery: "Discovery",
  seed_enrichment: "Seed Enrichment",
};

export function PipelineListPage() {
  const { clientId } = useParams<{ clientId: string }>();

  const clientQuery = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => getClient(clientId!),
    enabled: !!clientId,
  });

  const pipelinesQuery = useQuery({
    queryKey: ["clients", clientId, "pipelines"],
    queryFn: () => listPipelines(clientId!),
    enabled: !!clientId,
  });

  if (pipelinesQuery.isLoading || clientQuery.isLoading) {
    return (
      <div aria-busy="true" aria-label="Loading pipelines">
        <div className="skeleton h-8 w-48 mb-6" />
        {[1, 2].map((i) => <div key={i} className="skeleton h-12 w-full mb-2" />)}
      </div>
    );
  }

  if (pipelinesQuery.isError) {
    const msg = pipelinesQuery.error instanceof ApiError
      ? pipelinesQuery.error.message
      : "Failed to load pipelines";
    return <div role="alert" className="alert alert-error"><span>{msg}</span></div>;
  }

  const client = clientQuery.data;
  const pipelines = pipelinesQuery.data ?? [];

  return (
    <div>
      <div className="flex items-center gap-2 mb-6 text-sm text-base-content/60">
        <Link to="/clients">Clients</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}`}>{client?.name ?? clientId}</Link>
        <span>/</span>
        <span>Pipelines</span>
      </div>

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold">Pipelines</h1>
        <Link to={`/clients/${clientId}/pipelines/new`} className="btn btn-primary btn-sm">
          <Plus className="w-4 h-4" />
          New pipeline
        </Link>
      </div>

      {!pipelines.length ? (
        <div className="text-center py-16 text-base-content/60">
          <p className="mb-4">No pipelines yet.</p>
          <Link to={`/clients/${clientId}/pipelines/new`} className="btn btn-primary btn-sm">
            Create your first pipeline
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="table table-zebra w-full">
            <thead>
              <tr>
                <th>Name</th>
                <th>Lane</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {pipelines.map((p) => (
                <tr key={p.id}>
                  <td className="font-medium">{p.name}</td>
                  <td>
                    <span className="badge badge-info badge-sm">
                      {LANE_LABEL[p.lane] ?? p.lane}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-sm ${p.status === "active" ? "badge-success" : "badge-neutral"}`}>
                      {p.status}
                    </span>
                  </td>
                  <td>
                    <Link to={`/clients/${clientId}/pipelines/${p.id}`} className="btn btn-ghost btn-xs">
                      View
                    </Link>
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
