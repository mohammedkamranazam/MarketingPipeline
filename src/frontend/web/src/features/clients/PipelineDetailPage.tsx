/**
 * Acceptance Criteria:
 * - Shows pipeline objective (name, lane, status, description).
 * - Shows active config version and last run placeholders.
 * - Links to pipeline settings.
 * - Shows loading skeleton and error states.
 * - No TypeScript `any`.
 */
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { getPipeline, getClient } from "../../services/clientService";
import { ApiError } from "../../services/apiClient";

export function PipelineDetailPage() {
  const { clientId, pipelineId } = useParams<{ clientId: string; pipelineId: string }>();

  const clientQuery = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => getClient(clientId!),
    enabled: !!clientId,
  });

  const pipelineQuery = useQuery({
    queryKey: ["clients", clientId, "pipelines", pipelineId],
    queryFn: () => getPipeline(clientId!, pipelineId!),
    enabled: !!clientId && !!pipelineId,
  });

  if (pipelineQuery.isLoading || clientQuery.isLoading) {
    return (
      <div aria-busy="true" aria-label="Loading pipeline">
        <div className="skeleton h-8 w-64 mb-4" />
        <div className="skeleton h-4 w-48 mb-2" />
        <div className="skeleton h-4 w-32" />
      </div>
    );
  }

  if (pipelineQuery.isError) {
    const is404 = pipelineQuery.error instanceof ApiError && pipelineQuery.error.status === 404;
    return (
      <div role="alert" className="alert alert-error">
        <span>{is404 ? "Pipeline not found." : "Failed to load pipeline."}</span>
      </div>
    );
  }

  const client = clientQuery.data;
  const pipeline = pipelineQuery.data;
  if (!pipeline) return null;

  return (
    <div>
      <div className="flex items-center gap-2 mb-6 text-sm text-base-content/60">
        <Link to="/clients">Clients</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}`}>{client?.name ?? clientId}</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}/pipelines`}>Pipelines</Link>
        <span>/</span>
        <span>{pipeline.name}</span>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">{pipeline.name}</h1>
        <div className="flex gap-2">
          <span className="badge badge-info badge-sm">{pipeline.lane}</span>
          <span className={`badge badge-sm ${pipeline.status === "active" ? "badge-success" : "badge-neutral"}`}>
            {pipeline.status}
          </span>
        </div>
      </div>

      {pipeline.description && (
        <p className="text-sm text-base-content/70 mb-4">{pipeline.description}</p>
      )}

      <dl className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm mb-6 max-w-sm">
        <dt className="text-base-content/60">Active config</dt>
        <dd className="text-base-content/40 italic">None yet</dd>
        <dt className="text-base-content/60">Last run</dt>
        <dd className="text-base-content/40 italic">No runs yet</dd>
      </dl>

      <Link to={`/clients/${clientId}/pipelines/${pipeline.id}/settings`} className="btn btn-ghost btn-sm">
        Pipeline settings
      </Link>
    </div>
  );
}
