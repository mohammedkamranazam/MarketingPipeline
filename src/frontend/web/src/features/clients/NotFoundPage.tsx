/**
 * Acceptance Criteria:
 * - Displays a 404 message with a link back to clients.
 * - No TypeScript `any`.
 */
import { Link } from "react-router";

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-64 gap-4 text-center">
      <h1 className="text-3xl font-bold text-base-content/30">404</h1>
      <p className="text-base-content/60">Page not found.</p>
      <Link to="/clients" className="btn btn-primary btn-sm">
        Back to clients
      </Link>
    </div>
  );
}
