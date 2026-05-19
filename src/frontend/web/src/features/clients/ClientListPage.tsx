/**
 * Acceptance Criteria:
 * - Shows loading skeleton while fetching.
 * - Shows empty state when no clients exist with a link to create one.
 * - Shows list of clients with name, slug, status badge, and link to detail.
 * - Shows error state when the request fails.
 * - No TypeScript `any`.
 */
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { Plus } from "lucide-react";
import { listClients } from "../../services/clientService";
import { ApiError } from "../../services/apiClient";

export function ClientListPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["clients"],
    queryFn: listClients,
  });

  if (isLoading) {
    return (
      <div aria-busy="true" aria-label="Loading clients">
        <div className="skeleton h-8 w-48 mb-6" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="skeleton h-12 w-full mb-2" />
        ))}
      </div>
    );
  }

  if (isError) {
    const msg =
      error instanceof ApiError ? error.message : "Failed to load clients";
    return (
      <div role="alert" className="alert alert-error">
        <span>{msg}</span>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold">Clients</h1>
        <Link to="/clients/new" className="btn btn-primary btn-sm">
          <Plus className="w-4 h-4" />
          New client
        </Link>
      </div>

      {!data?.length ? (
        <div className="text-center py-16 text-base-content/60">
          <p className="mb-4">No clients yet.</p>
          <Link to="/clients/new" className="btn btn-primary btn-sm">
            Create your first client
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="table table-zebra w-full">
            <thead>
              <tr>
                <th>Name</th>
                <th>Slug</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data.map((client) => (
                <tr key={client.id}>
                  <td className="font-medium">{client.name}</td>
                  <td className="text-base-content/60 text-sm">{client.slug}</td>
                  <td>
                    <span
                      className={`badge badge-sm ${
                        client.status === "active"
                          ? "badge-success"
                          : "badge-neutral"
                      }`}
                    >
                      {client.status}
                    </span>
                  </td>
                  <td>
                    <Link
                      to={`/clients/${client.id}`}
                      className="btn btn-ghost btn-xs"
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
