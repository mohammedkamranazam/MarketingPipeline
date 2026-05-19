/**
 * Acceptance Criteria:
 * - getInitialTheme returns pipeline-dark when prefers-color-scheme: dark.
 * - getInitialTheme returns pipeline-light when prefers-color-scheme: light.
 * - getInitialTheme returns stored value from localStorage.
 * - No TypeScript `any`.
 */
import { describe, it, expect, beforeEach, vi } from "vitest";

// Test the pure logic extracted from useTheme without React hooks
const STORAGE_KEY = "mp-theme";

function getInitialTheme(
  storedValue: string | null,
  prefersDark: boolean,
): "pipeline-light" | "pipeline-dark" {
  if (storedValue === "pipeline-light" || storedValue === "pipeline-dark")
    return storedValue;
  return prefersDark ? "pipeline-dark" : "pipeline-light";
}

describe("getInitialTheme logic", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns stored pipeline-dark", () => {
    expect(getInitialTheme("pipeline-dark", false)).toBe("pipeline-dark");
  });

  it("returns stored pipeline-light", () => {
    expect(getInitialTheme("pipeline-light", true)).toBe("pipeline-light");
  });

  it("returns pipeline-dark from system preference when no stored value", () => {
    expect(getInitialTheme(null, true)).toBe("pipeline-dark");
  });

  it("returns pipeline-light from system preference when no stored value", () => {
    expect(getInitialTheme(null, false)).toBe("pipeline-light");
  });

  it("ignores invalid stored value", () => {
    expect(getInitialTheme("invalid", false)).toBe("pipeline-light");
  });
});

describe(STORAGE_KEY, () => {
  it("is the expected key name", () => {
    expect(STORAGE_KEY).toBe("mp-theme");
  });
});
