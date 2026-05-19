/**
 * Acceptance Criteria:
 * - Lists all source connectors for the pipeline.
 * - Shows loading state while fetching.
 * - Shows empty state when no connectors exist.
 * - Shows error state on fetch failure.
 * - "Add Connector" button navigates to /sources/new.
 * - Each connector shows name, source_type, adapter_key, and status badge.
 * - Clicking a connector row navigates to /sources/:connectorId.
 * - No TypeScript `any`.
 */
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router";
import { listSourceConnectors } from "../../services/sourceService";

export function SourceRegistryPage() {
  const { clientId, pipelineId } = useParams<{
    clientId: string;
    pipelineId: string;
  }>();
  const navigate = useNavigate();

  const { data: connectors, isLoading, isError } = useQuery({
    queryKey: ["sources", clientId, pipelineId],
    queryFn: () => listSourceConnectors(clientId!, pipelineId!),
    enabled: Boolean(clientId && pipelineId),
  });

  const base = `/clients/${clientId}/pipelines/${pipelineId}`;

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="skeleton h-8 w-48 mb-4" />
        <div className="skeleton h-24 w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-6">
        <div className="alert alert-error">
          <span>Failed to load source connectors.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Source Registry</h1>
        <Link to={`${base}/sources/new`} className="btn btn-primary btn-sm">
          Add Connector
        </Link>
      </div>

      {connectors?.length === 0 ? (
        <div className="text-center py-12 text-base-content/50">
          No source connectors configured. Add one to begin.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="table table-zebra w-full">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Adapter</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {connectors?.map((connector) => (
                <tr
                  key={connector.id}
                  className="cursor-pointer hover"
                  onClick={() => void navigate(`${base}/sources/${connector.id}`)}
                >
                  <td className="font-medium">{connector.name}</td>
                  <td className="capitalize">{connector.source_type.replace(/_/g, " ")}</td>
                  <td>
                    <code className="text-sm">{connector.adapter_key}</code>
                  </td>
                  <td>
                    <StatusBadge status={connector.status} />
                  </td>
                  <td>
                    <Link
                      to={`${base}/sources/${connector.id}`}
                      className="btn btn-ghost btn-xs"
                      onClick={(e) => e.stopPropagation()}
                    >
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

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: "badge-success",
    paused: "badge-warning",
    error: "badge-error",
    disabled: "badge-ghost",
  };
  return (
    <span className={`badge badge-sm ${colors[status] ?? "badge-ghost"}`}>
      {status}
    </span>
  );
}
