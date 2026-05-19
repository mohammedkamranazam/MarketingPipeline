/**
 * Acceptance Criteria:
 * - Imports @testing-library/jest-dom matchers for extended DOM assertions.
 * - Starts MSW server before all tests and resets/closes after.
 */
import "@testing-library/jest-dom";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./msw/server";


beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
