/**
 * Acceptance Criteria:
 * - Returns current theme name and a toggle function.
 * - Persists theme preference in localStorage.
 * - Applies data-theme attribute to document.documentElement.
 * - Defaults to system preference: pipeline-dark if prefers-color-scheme: dark.
 * - No TypeScript `any`.
 */
import { useEffect, useState } from "react";

type Theme = "pipeline-light" | "pipeline-dark";

const STORAGE_KEY = "mp-theme";

function getInitialTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "pipeline-light" || stored === "pipeline-dark") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "pipeline-dark"
    : "pipeline-light";
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  function toggle() {
    setTheme((t) =>
      t === "pipeline-light" ? "pipeline-dark" : "pipeline-light",
    );
  }

  return { theme, toggle };
}
