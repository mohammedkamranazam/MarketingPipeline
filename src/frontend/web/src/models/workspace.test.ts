/**
 * Acceptance Criteria:
 * - toWorkspaceSummary maps ClientResponse to WorkspaceSummary.
 * - toPipelineSummary maps PipelineResponse to PipelineSummary.
 */
import { describe, it, expect } from "vitest";
import { toWorkspaceSummary, toPipelineSummary } from "./workspace";
import type { ClientResponse, PipelineResponse } from "../contracts/clients";

const NOW = new Date().toISOString();

const client: ClientResponse = {
  id: "11111111-1111-1111-1111-111111111111",
  name: "tec5USA",
  slug: "tec5usa",
  status: "active",
  created_at: NOW,
  updated_at: NOW,
};

const pipeline: PipelineResponse = {
  id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  client_id: client.id,
  name: "Discovery",
  slug: "discovery",
  lane: "discovery",
  status: "active",
  description: "Test pipeline",
  created_at: NOW,
  updated_at: NOW,
};

describe("toWorkspaceSummary", () => {
  it("maps required fields", () => {
    const summary = toWorkspaceSummary(client);
    expect(summary.id).toBe(client.id);
    expect(summary.name).toBe("tec5USA");
    expect(summary.slug).toBe("tec5usa");
    expect(summary.status).toBe("active");
  });
});

describe("toPipelineSummary", () => {
  it("maps required fields including clientId", () => {
    const summary = toPipelineSummary(pipeline);
    expect(summary.id).toBe(pipeline.id);
    expect(summary.clientId).toBe(client.id);
    expect(summary.lane).toBe("discovery");
    expect(summary.description).toBe("Test pipeline");
  });

  it("maps null description", () => {
    const summary = toPipelineSummary({ ...pipeline, description: null });
    expect(summary.description).toBeNull();
  });
});
