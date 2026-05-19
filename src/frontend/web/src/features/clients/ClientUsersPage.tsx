/**
 * Acceptance Criteria:
 * - Route is complete and renders a placeholder until user APIs are available.
 * - Shows breadcrumb back to client detail.
 * - No TypeScript `any`.
 */
import { Link, useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { getClient } from "../../services/clientService";

export function ClientUsersPage() {
  const { clientId } = useParams<{ clientId: string }>();
  const { data } = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => getClient(clientId!),
    enabled: !!clientId,
  });

  return (
    <div>
      <div className="flex items-center gap-2 mb-6 text-sm text-base-content/60">
        <Link to="/clients">Clients</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}`}>{data?.name ?? clientId}</Link>
        <span>/</span>
        <span>Users</span>
      </div>
      <h1 className="text-xl font-semibold mb-4">Users</h1>
      <div className="text-base-content/60 py-12 text-center text-sm">
        User management will be available in a future phase.
      </div>
    </div>
  );
}
