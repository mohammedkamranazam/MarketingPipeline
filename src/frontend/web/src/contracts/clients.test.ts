/**
 * Acceptance Criteria:
 * - ClientResponseSchema parses valid client data.
 * - ClientResponseSchema rejects missing fields.
 * - PipelineResponseSchema parses valid pipeline data.
 * - PipelineResponseSchema rejects invalid lane values.
 * - ClientListResponseSchema parses array of clients.
 */
import { describe, expect, it } from "vitest";
import {
  ClientResponseSchema,
  ClientListResponseSchema,
  PipelineResponseSchema,
} from "./clients";

const NOW = new Date().toISOString();

const validClient = {
  id: "11111111-1111-1111-1111-111111111111",
  name: "tec5USA",
  slug: "tec5usa",
  status: "active",
  created_at: NOW,
  updated_at: NOW,
};

const validPipeline = {
  id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  client_id: validClient.id,
  name: "Discovery 2024",
  slug: "discovery-2024",
  lane: "discovery",
  status: "active",
  description: null,
  created_at: NOW,
  updated_at: NOW,
};

describe("ClientResponseSchema", () => {
  it("parses valid client", () => {
    expect(ClientResponseSchema.parse(validClient)).toMatchObject({ name: "tec5USA" });
  });

  it("rejects missing id", () => {
    expect(() => ClientResponseSchema.parse({ ...validClient, id: undefined })).toThrow();
  });

  it("rejects empty id", () => {
    expect(() => ClientResponseSchema.parse({ ...validClient, id: "" })).toThrow();
  });
});

describe("ClientListResponseSchema", () => {
  it("parses array of clients", () => {
    expect(ClientListResponseSchema.parse([validClient])).toHaveLength(1);
  });

  it("parses empty array", () => {
    expect(ClientListResponseSchema.parse([])).toHaveLength(0);
  });
});

describe("PipelineResponseSchema", () => {
  it("parses valid pipeline", () => {
    expect(PipelineResponseSchema.parse(validPipeline)).toMatchObject({ lane: "discovery" });
  });

  it("parses seed_enrichment lane", () => {
    expect(
      PipelineResponseSchema.parse({ ...validPipeline, lane: "seed_enrichment" }),
    ).toMatchObject({ lane: "seed_enrichment" });
  });

  it("rejects invalid lane", () => {
    expect(() =>
      PipelineResponseSchema.parse({ ...validPipeline, lane: "other" }),
    ).toThrow();
  });

  it("accepts null description", () => {
    expect(PipelineResponseSchema.parse({ ...validPipeline, description: null })).toMatchObject({
      description: null,
    });
  });
});
