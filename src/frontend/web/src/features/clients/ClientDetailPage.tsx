/**
 * Acceptance Criteria:
 * - Shows workspace metadata: name, slug, status, created_at, updated_at.
 * - Shows nav links to settings, users, and pipelines sub-sections.
 * - Shows loading skeleton while fetching.
 * - Shows 404 message when client is not found (ApiError 404).
 * - Shows generic error state for other failures.
 * - No TypeScript `any`.
 */
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { getClient } from "../../services/clientService";
import { ApiError } from "../../services/apiClient";

export function ClientDetailPage() {
  const { clientId } = useParams<{ clientId: string }>();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => getClient(clientId!),
    enabled: !!clientId,
  });

  if (isLoading) {
    return (
      <div aria-busy="true" aria-label="Loading client">
        <div className="skeleton h-8 w-64 mb-4" />
        <div className="skeleton h-4 w-48 mb-2" />
        <div className="skeleton h-4 w-32" />
      </div>
    );
  }

  if (isError) {
    const is404 = error instanceof ApiError && error.status === 404;
    return (
      <div role="alert" className="alert alert-error">
        <span>{is404 ? "Client not found." : "Failed to load client."}</span>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div>
      <div className="flex items-center gap-2 mb-6 text-sm text-base-content/60">
        <Link to="/clients">Clients</Link>
        <span>/</span>
        <span>{data.name}</span>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">{data.name}</h1>
        <span
          className={`badge ${data.status === "active" ? "badge-success" : "badge-neutral"}`}
        >
          {data.status}
        </span>
      </div>

      <dl className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm mb-6 max-w-sm">
        <dt className="text-base-content/60">Slug</dt>
        <dd className="font-mono">{data.slug}</dd>
        <dt className="text-base-content/60">Created</dt>
        <dd>{new Date(data.created_at).toLocaleDateString()}</dd>
        <dt className="text-base-content/60">Updated</dt>
        <dd>{new Date(data.updated_at).toLocaleDateString()}</dd>
      </dl>

      <div className="flex gap-3">
        <Link to={`/clients/${data.id}/pipelines`} className="btn btn-primary btn-sm">
          Pipelines
        </Link>
        <Link to={`/clients/${data.id}/settings`} className="btn btn-ghost btn-sm">
          Settings
        </Link>
        <Link to={`/clients/${data.id}/users`} className="btn btn-ghost btn-sm">
          Users
        </Link>
      </div>
    </div>
  );
}
