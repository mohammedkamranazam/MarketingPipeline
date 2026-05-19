/**
 * Acceptance Criteria:
 * - Lists crawl jobs with status badges (queued, running, paused, failed, retrying,
 *   completed, blocked, stale, cancelled).
 * - Provides "New Job" form to create a crawl job.
 * - "Run" button triggers runCrawlJob for queued/paused jobs.
 * - "Cancel" button cancels non-terminal jobs.
 * - Polls every 5 seconds while any job is in a non-terminal state.
 * - Polling strategy: polling-first with 5s interval; SSE upgrade path documented below.
 * - Loading, empty, and error states are handled.
 * - No TypeScript `any`.
 *
 * Polling strategy:
 *   Current: useQuery with refetchInterval=5000 (polling-first).
 *   SSE upgrade path: when backend exposes GET /crawl-jobs/stream, replace polling
 *   with an EventSource subscription and call queryClient.setQueryData on each event.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router";
import type { CrawlJobResponse } from "../../contracts/crawl";
import {
  cancelCrawlJob,
  createCrawlJob,
  listCrawlJobs,
  runCrawlJob,
} from "../../services/crawlService";

const TERMINAL = new Set(["completed", "failed", "cancelled", "blocked"]);

function statusBadge(status: CrawlJobResponse["status"]) {
  const colorMap: Record<string, string> = {
    queued: "badge-info",
    running: "badge-primary",
    paused: "badge-warning",
    failed: "badge-error",
    retrying: "badge-warning",
    completed: "badge-success",
    blocked: "badge-error",
    stale: "badge-neutral",
    cancelled: "badge-neutral",
  };
  return (
    <span className={`badge badge-sm ${colorMap[status] ?? "badge-neutral"}`}>
      {status}
    </span>
  );
}

export default function CrawlRunMonitorPage() {
  const { clientId, pipelineId } = useParams<{
    clientId: string;
    pipelineId: string;
  }>();
  const queryClient = useQueryClient();

  const {
    data: jobs = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["crawl-jobs", clientId, pipelineId],
    queryFn: () => listCrawlJobs(clientId!, pipelineId!),
    enabled: !!clientId && !!pipelineId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      return data.some((j) => !TERMINAL.has(j.status)) ? 5000 : false;
    },
  });

  const createMutation = useMutation({
    mutationFn: () => createCrawlJob(clientId!, pipelineId!, { job_type: "crawl" }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["crawl-jobs", clientId, pipelineId] }),
  });

  const cancelMutation = useMutation({
    mutationFn: (jobId: string) => cancelCrawlJob(clientId!, pipelineId!, jobId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["crawl-jobs", clientId, pipelineId] }),
  });

  const runMutation = useMutation({
    mutationFn: ({ jobId, url }: { jobId: string; url: string }) =>
      runCrawlJob(clientId!, pipelineId!, jobId, url),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["crawl-jobs", clientId, pipelineId] }),
  });

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
        <span>Failed to load crawl jobs.</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Crawl Job Monitor</h1>
        <button
          className="btn btn-primary btn-sm"
          onClick={() => createMutation.mutate()}
          disabled={createMutation.isPending}
        >
          {createMutation.isPending ? "Creating…" : "New Job"}
        </button>
      </div>

      {createMutation.isError && (
        <div role="alert" className="alert alert-error">
          <span>Failed to create job.</span>
        </div>
      )}

      {jobs.length === 0 ? (
        <div className="text-center py-16 text-base-content/50">
          No crawl jobs yet. Click &ldquo;New Job&rdquo; to start one.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="table table-zebra w-full">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Attempt</th>
                <th>Scheduled</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.id}>
                  <td className="font-mono text-xs">{job.id.slice(0, 8)}…</td>
                  <td>{job.job_type}</td>
                  <td>{statusBadge(job.status)}</td>
                  <td>
                    {job.attempt} / {job.max_attempts}
                  </td>
                  <td className="text-xs">{new Date(job.scheduled_at).toLocaleString()}</td>
                  <td className="flex gap-2">
                    {(job.status === "queued" || job.status === "paused") && (
                      <button
                        className="btn btn-xs btn-success"
                        onClick={() =>
                          runMutation.mutate({ jobId: job.id, url: "https://example.com" })
                        }
                        disabled={runMutation.isPending}
                      >
                        Run
                      </button>
                    )}
                    {!TERMINAL.has(job.status) && (
                      <button
                        className="btn btn-xs btn-error"
                        onClick={() => cancelMutation.mutate(job.id)}
                        disabled={cancelMutation.isPending}
                      >
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
