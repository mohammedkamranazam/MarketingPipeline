/**
 * Acceptance Criteria:
 * - Renders a sidebar, topbar, and main content region via <Outlet/>.
 * - Sidebar shows navigation links for Clients.
 * - Topbar shows app title and theme toggle.
 * - Theme toggle switches between pipeline-light and pipeline-dark via data-theme on <html>.
 * - No TypeScript `any`.
 */
import { Outlet, NavLink } from "react-router";
import { LayoutDashboard, Moon, Sun } from "lucide-react";
import { useTheme } from "../../hooks/useTheme";

export function AppShell() {
  const { theme, toggle } = useTheme();

  return (
    <div className="drawer lg:drawer-open min-h-screen">
      <input id="main-drawer" type="checkbox" className="drawer-toggle" />

      {/* Page content */}
      <div className="drawer-content flex flex-col">
        {/* Topbar */}
        <header className="navbar bg-base-200 border-b border-base-300 px-4 lg:px-6">
          <div className="flex-none lg:hidden">
            <label
              htmlFor="main-drawer"
              aria-label="Open navigation"
              className="btn btn-ghost btn-square"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </label>
          </div>
          <div className="flex-1">
            <span className="font-semibold text-base-content tracking-tight">
              Marketing Pipeline
            </span>
          </div>
          <div className="flex-none">
            <button
              className="btn btn-ghost btn-square"
              onClick={toggle}
              aria-label={
                theme === "pipeline-dark"
                  ? "Switch to light theme"
                  : "Switch to dark theme"
              }
            >
              {theme === "pipeline-dark" ? (
                <Sun className="w-4 h-4" />
              ) : (
                <Moon className="w-4 h-4" />
              )}
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 p-4 lg:p-6 bg-base-100">
          <Outlet />
        </main>
      </div>

      {/* Sidebar */}
      <nav className="drawer-side z-40">
        <label
          htmlFor="main-drawer"
          aria-label="Close navigation"
          className="drawer-overlay"
        />
        <aside className="menu bg-base-200 min-h-full w-60 p-4 gap-1">
          <div className="mb-4 px-2">
            <span className="font-bold text-sm text-base-content/70 uppercase tracking-wider">
              Admin
            </span>
          </div>
          <NavLink
            to="/clients"
            className={({ isActive }) =>
              `menu-item flex items-center gap-2 rounded-btn px-3 py-2 text-sm ${
                isActive
                  ? "bg-primary text-primary-content"
                  : "hover:bg-base-300"
              }`
            }
          >
            <LayoutDashboard className="w-4 h-4" />
            Clients
          </NavLink>
        </aside>
      </nav>
    </div>
  );
}
