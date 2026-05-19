/**
 * Tests for ingestionService.
 *
 * Acceptance criteria:
 * - listDocuments returns list of DocumentResponse from MSW handler.
 * - getDocument returns a single DocumentResponse.
 * - listLeadImports returns list of LeadImportBatchResponse.
 * - getLeadImport returns a single batch.
 * - listSeedLeadRows returns list of SeedLeadRowResponse.
 * - listDocuments returns [] for pipeline with no documents.
 * - listLeadImports returns [] for pipeline with no imports.
 */
import { describe, expect, it } from "vitest";
import {
  FIXTURE_BATCH,
  FIXTURE_DOCUMENT,
  FIXTURE_PIPELINE_A,
  FIXTURE_PIPELINE_B,
  FIXTURE_CLIENT,
  FIXTURE_ROW,
} from "../test/msw/handlers";
import {
  listDocuments,
  getDocument,
  listLeadImports,
  getLeadImport,
  listSeedLeadRows,
} from "./ingestionService";

const CID = FIXTURE_CLIENT.id;
const PID_A = FIXTURE_PIPELINE_A.id;
const PID_B = FIXTURE_PIPELINE_B.id;
const DOC_ID = FIXTURE_DOCUMENT.id;
const BATCH_ID = FIXTURE_BATCH.id;

describe("listDocuments", () => {
  it("returns documents for pipeline A", async () => {
    const docs = await listDocuments(CID, PID_A);
    expect(docs).toHaveLength(1);
    expect(docs[0]?.id).toBe(DOC_ID);
  });

  it("returns empty list for pipeline without documents", async () => {
    const docs = await listDocuments(CID, PID_B);
    expect(docs).toEqual([]);
  });
});

describe("getDocument", () => {
  it("returns document by id", async () => {
    const doc = await getDocument(CID, PID_A, DOC_ID);
    expect(doc.id).toBe(DOC_ID);
    expect(doc.status).toBe("parsed");
  });
});

describe("listLeadImports", () => {
  it("returns batches for pipeline B", async () => {
    const batches = await listLeadImports(CID, PID_B);
    expect(batches).toHaveLength(1);
    expect(batches[0]?.id).toBe(BATCH_ID);
  });

  it("returns empty list for pipeline without imports", async () => {
    const batches = await listLeadImports(CID, PID_A);
    expect(batches).toEqual([]);
  });
});

describe("getLeadImport", () => {
  it("returns batch by id", async () => {
    const batch = await getLeadImport(CID, PID_B, BATCH_ID);
    expect(batch.id).toBe(BATCH_ID);
    expect(batch.total_rows).toBe(3);
  });
});

describe("listSeedLeadRows", () => {
  it("returns rows for batch", async () => {
    const rows = await listSeedLeadRows(CID, PID_B, BATCH_ID);
    expect(rows).toHaveLength(1);
    expect(rows[0]?.id).toBe(FIXTURE_ROW.id);
    expect(rows[0]?.normalized_first_name).toBe("Alice");
  });
});

describe("uploadDocument", () => {
  it("uploads a file and returns DocumentResponse", async () => {
    const { uploadDocument } = await import("./ingestionService");
    const file = new File([new Uint8Array([104, 105])], "test.txt", { type: "text/plain" });
    const result = await uploadDocument(CID, PID_A, file);
    expect(result.id).toBe(DOC_ID);
    expect(result.status).toBe("parsed");
  });
});

describe("uploadLeadImport", () => {
  it("uploads a CSV and returns LeadImportBatchResponse", async () => {
    const { uploadLeadImport } = await import("./ingestionService");
    const file = new File(["first_name,company\nAlice,Acme"], "leads.csv", {
      type: "text/csv",
    });
    const result = await uploadLeadImport(CID, PID_B, file);
    expect(result.id).toBe(BATCH_ID);
    expect(result.total_rows).toBe(3);
  });

  it("throws on 422 response", async () => {
    const { http, HttpResponse } = await import("msw");
    const { server } = await import("../test/msw/server");
    server.use(
      http.post(
        `http://localhost/clients/${CID}/pipelines/${PID_B}/lead-imports`,
        () => HttpResponse.json({ detail: "Unsupported" }, { status: 422 }),
      ),
    );
    const { uploadLeadImport: upload } = await import("./ingestionService");
    const file = new File(["data"], "bad.pdf", { type: "application/pdf" });
    await expect(upload(CID, PID_B, file)).rejects.toThrow("Unsupported");
  });
});
