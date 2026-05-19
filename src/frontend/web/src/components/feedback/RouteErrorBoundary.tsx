/**
 * Acceptance Criteria:
 * - Catches render errors in child routes and displays a fallback UI.
 * - Shows error message and a retry button that reloads the page.
 * - No TypeScript `any`.
 */
import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export class RouteErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div
          role="alert"
          className="flex flex-col items-center justify-center min-h-64 gap-4 text-center"
        >
          <p className="text-error font-semibold">Something went wrong</p>
          <p className="text-sm text-base-content/70">
            {this.state.error.message}
          </p>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
