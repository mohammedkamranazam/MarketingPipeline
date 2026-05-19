/**
 * Acceptance Criteria:
 * - Lists crawl artifacts with type, URL, status, content_hash, size, policy_decision.
 * - Shows lineage: crawl_job_id and seed_lead_row_id when present.
 * - "Robots Check" panel lets users test a URL for robots.txt compliance.
 * - Artifact rows show policy_decision badge (allow/block/review).
 * - Large artifact lists: note on table virtualization displayed when >100 rows.
 * - Loading, empty, and error states handled.
 * - No TypeScript `any`.
 *
 * Table virtualization note:
 *   When artifact count exceeds 100, a notice is shown. For production-scale pipelines,
 *   replace this table with @tanstack/react-virtual to avoid DOM overload.
 */
import { useMutation, useQuery } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { useParams } from "react-router";
import type { CrawlArtifactResponse, RobotsCheckResult } from "../../contracts/crawl";
import { checkRobots, listArtifacts } from "../../services/crawlService";

const VIRTUALIZATION_THRESHOLD = 100;

function policyBadge(decision: string | null) {
  if (!decision) return null;
  const colorMap: Record<string, string> = {
    allow: "badge-success",
    block: "badge-error",
    review: "badge-warning",
  };
  return (
    <span className={`badge badge-sm ${colorMap[decision] ?? "badge-neutral"}`}>
      {decision}
    </span>
  );
}

function ArtifactRow({ artifact }: { artifact: CrawlArtifactResponse }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <tr
        className="cursor-pointer hover"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <td className="font-mono text-xs">{artifact.id.slice(0, 8)}…</td>
        <td>{artifact.artifact_type}</td>
        <td className="text-xs max-w-xs truncate">{artifact.url ?? "—"}</td>
        <td>{artifact.status}</td>
        <td>{policyBadge(artifact.policy_decision)}</td>
        <td className="font-mono text-xs">{artifact.content_hash?.slice(0, 12) ?? "—"}</td>
        <td>{artifact.size_bytes != null ? `${artifact.size_bytes} B` : "—"}</td>
      </tr>
      {open && (
        <tr>
          <td colSpan={7} className="bg-base-200 p-4 text-sm space-y-1">
            <p>
              <strong>Full ID:</strong>{" "}
              <span className="font-mono text-xs">{artifact.id}</span>
            </p>
            <p>
              <strong>Storage key:</strong>{" "}
              <span className="font-mono text-xs">{artifact.storage_key}</span>
            </p>
            <p>
              <strong>Content hash:</strong>{" "}
              <span className="font-mono text-xs">{artifact.content_hash ?? "—"}</span>
            </p>
            <p>
              <strong>MIME type:</strong> {artifact.mime_type ?? "—"}
            </p>
            <p>
              <strong>Crawl job:</strong>{" "}
              <span className="font-mono text-xs">{artifact.crawl_job_id ?? "—"}</span>
            </p>
            <p>
              <strong>Seed lead row:</strong>{" "}
              <span className="font-mono text-xs">{artifact.seed_lead_row_id ?? "—"}</span>
            </p>
          </td>
        </tr>
      )}
    </>
  );
}

export default function ArtifactInspectorPage() {
  const { clientId, pipelineId } = useParams<{
    clientId: string;
    pipelineId: string;
  }>();
  const robotsUrlRef = useRef<HTMLInputElement>(null);
  const [robotsResult, setRobotsResult] = useState<RobotsCheckResult | null>(null);

  const {
    data: artifacts = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["artifacts", clientId, pipelineId],
    queryFn: () => listArtifacts(clientId!, pipelineId!),
    enabled: !!clientId && !!pipelineId,
  });

  const robotsMutation = useMutation({
    mutationFn: (url: string) => checkRobots(clientId!, pipelineId!, url),
    onSuccess: (result) => setRobotsResult(result),
  });

  const handleRobotsCheck = () => {
    const url = robotsUrlRef.current?.value.trim();
    if (url) robotsMutation.mutate(url);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <span className="loading loading-spinner loading-lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" className="alert alert-error m-4">
        <span>Failed to load artifacts.</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Artifact Inspector</h1>

      {/* Robots Check Panel */}
      <div className="card bg-base-200 p-4 space-y-3">
        <h2 className="font-semibold">Robots.txt Check</h2>
        <div className="flex gap-2">
          <input
            ref={robotsUrlRef}
            type="url"
            placeholder="https://example.com/page"
            className="input input-bordered input-sm flex-1"
            aria-label="URL to check"
          />
          <button
            className="btn btn-sm btn-secondary"
            onClick={handleRobotsCheck}
            disabled={robotsMutation.isPending}
          >
            {robotsMutation.isPending ? "Checking…" : "Check"}
          </button>
        </div>
        {robotsResult && (
          <div
            role="alert"
            className={`alert alert-sm ${robotsResult.allowed ? "alert-success" : "alert-error"}`}
          >
            <span>
              {robotsResult.allowed
                ? `Allowed: ${robotsResult.url}`
                : `Blocked: ${robotsResult.url} — ${robotsResult.reason}`}
            </span>
          </div>
        )}
      </div>

      {/* Artifact Table */}
      {artifacts.length === 0 ? (
        <div className="text-center py-16 text-base-content/50">No artifacts found.</div>
      ) : (
        <>
          {artifacts.length > VIRTUALIZATION_THRESHOLD && (
            <div role="note" className="alert alert-info text-sm">
              <span>
                Showing {artifacts.length} artifacts. For large pipelines, consider enabling
                virtual scrolling via @tanstack/react-virtual.
              </span>
            </div>
          )}
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>URL</th>
                  <th>Status</th>
                  <th>Policy</th>
                  <th>Hash</th>
                  <th>Size</th>
                </tr>
              </thead>
              <tbody>
                {artifacts.map((artifact) => (
                  <ArtifactRow key={artifact.id} artifact={artifact} />
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
