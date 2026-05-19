/**
 * Acceptance Criteria:
 * - listClients() returns validated array from GET /clients.
 * - getClient() returns validated client by id.
 * - getClient() throws ApiError on 404.
 * - createClient() posts and returns validated response.
 * - updateClient() patches and returns validated response.
 * - listPipelines() returns validated array.
 * - getPipeline() returns validated pipeline.
 * - createPipeline() posts and returns validated response.
 * - updatePipeline() patches and returns validated response.
 */
import { describe, expect, it } from "vitest";
import {
  listClients,
  getClient,
  createClient,
  updateClient,
  listPipelines,
  getPipeline,
  createPipeline,
  updatePipeline,
} from "./clientService";
import { ApiError } from "./apiClient";
import { FIXTURE_CLIENT, FIXTURE_PIPELINE_A } from "../test/msw/handlers";

describe("listClients", () => {
  it("returns validated array", async () => {
    const clients = await listClients();
    expect(clients).toHaveLength(1);
    expect(clients[0]?.name).toBe("tec5USA");
  });
});

describe("getClient", () => {
  it("returns client by id", async () => {
    const c = await getClient(FIXTURE_CLIENT.id);
    expect(c.id).toBe(FIXTURE_CLIENT.id);
  });

  it("throws ApiError 404 for unknown id", async () => {
    await expect(getClient("00000000-0000-0000-0000-000000000000")).rejects.toBeInstanceOf(
      ApiError,
    );
  });
});

describe("createClient", () => {
  it("creates and returns a client", async () => {
    const c = await createClient({ name: "New Client", slug: "new-client" });
    expect(c.name).toBe("New Client");
    expect(c.id).toBeDefined();
  });
});

describe("updateClient", () => {
  it("patches and returns updated client", async () => {
    const c = await updateClient(FIXTURE_CLIENT.id, { status: "inactive" });
    expect(c.status).toBe("inactive");
  });
});

describe("listPipelines", () => {
  it("returns pipelines for client", async () => {
    const pipelines = await listPipelines(FIXTURE_CLIENT.id);
    expect(pipelines).toHaveLength(2);
  });
});

describe("getPipeline", () => {
  it("returns pipeline by id", async () => {
    const p = await getPipeline(FIXTURE_CLIENT.id, FIXTURE_PIPELINE_A.id);
    expect(p.lane).toBe("discovery");
  });

  it("throws ApiError 404 for unknown pipeline", async () => {
    await expect(
      getPipeline(FIXTURE_CLIENT.id, "00000000-0000-0000-0000-000000000000"),
    ).rejects.toBeInstanceOf(ApiError);
  });
});

describe("createPipeline", () => {
  it("creates and returns a pipeline", async () => {
    const p = await createPipeline(FIXTURE_CLIENT.id, {
      name: "New Pipeline",
      slug: "new-pipeline",
      lane: "discovery",
    });
    expect(p.name).toBe("New Pipeline");
  });
});

describe("updatePipeline", () => {
  it("patches and returns updated pipeline", async () => {
    const p = await updatePipeline(FIXTURE_CLIENT.id, FIXTURE_PIPELINE_A.id, {
      status: "paused",
    });
    expect(p.status).toBe("paused");
  });
});
