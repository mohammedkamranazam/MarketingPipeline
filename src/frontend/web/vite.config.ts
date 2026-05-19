import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss(), react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    exclude: ["node_modules", "e2e/**"],
    env: {
      VITE_API_BASE: "http://localhost",
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      // Pages and components are covered by Playwright E2E smoke tests.
      // Unit coverage threshold applies to contracts, models, services, hooks.
      include: [
        "src/contracts/**/*.ts",
        "src/models/**/*.ts",
        "src/services/**/*.ts",
        "src/hooks/**/*.ts",
        "src/utils/**/*.ts",
      ],
      exclude: ["src/**/*.test.{ts,tsx}", "src/**/*.d.ts", "src/hooks/useTheme.ts"],
      thresholds: { lines: 80 },
    },
  },
});
