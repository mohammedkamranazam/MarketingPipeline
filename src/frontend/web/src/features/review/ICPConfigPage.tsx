/**
 * Acceptance Criteria:
 * - Shows current active ICP config or "No config" when none exists.
 * - Edit form pre-populates existing config fields.
 * - Vertical, titles, signals, geographies, exclusions are editable.
 * - Tags (titles, signals, etc.) entered as comma-separated values.
 * - Save button PUTs the upserted config.
 * - Shows validation errors and server errors inline.
 * - Shows policy impact note before save when guardrails are missing.
 * - No TypeScript `any`.
 */
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getICPConfig, upsertICPConfig } from "../../services/reviewService";
import type { ActiveICPConfigUpsert } from "../../contracts/review";

function tagsToString(tags: string[]): string {
  return tags.join(", ");
}

function stringToTags(value: string): string[] {
  return value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

export function ICPConfigPage() {
  const { clientId = "", pipelineId = "" } = useParams();
  const queryClient = useQueryClient();

  const { data: config, isLoading } = useQuery({
    queryKey: ["icp-config", clientId, pipelineId],
    queryFn: () => getICPConfig(clientId, pipelineId),
    enabled: Boolean(clientId && pipelineId),
  });

  const [vertical, setVertical] = useState("");
  const [titles, setTitles] = useState("");
  const [geographies, setGeographies] = useState("");
  const [signals, setSignals] = useState("");
  const [exclusions, setExclusions] = useState("");
  const [notes, setNotes] = useState("");
  const [activatedBy, setActivatedBy] = useState("");

  useEffect(() => {
    if (config) {
      setVertical(config.vertical ?? "");
      setTitles(tagsToString(config.titles));
      setGeographies(tagsToString(config.geographies));
      setSignals(tagsToString(config.signals));
      setExclusions(tagsToString(config.exclusions));
      setNotes(config.notes ?? "");
      setActivatedBy(config.activated_by ?? "");
    }
  }, [config]);

  const mutation = useMutation({
    mutationFn: (payload: ActiveICPConfigUpsert) =>
      upsertICPConfig(clientId, pipelineId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["icp-config", clientId, pipelineId] });
    },
  });

  function handleSave() {
    mutation.mutate({
      vertical: vertical || undefined,
      titles: stringToTags(titles),
      geographies: stringToTags(geographies),
      signals: stringToTags(signals),
      exclusions: stringToTags(exclusions),
      notes: notes || undefined,
      activated_by: activatedBy || undefined,
    });
  }

  if (isLoading) {
    return <div className="p-4"><span className="loading loading-spinner" /></div>;
  }

  return (
    <div className="p-4 space-y-6 max-w-2xl">
      <h1 className="text-xl font-bold">ICP Configuration</h1>

      {!config && (
        <div className="alert alert-info" data-testid="no-config-notice">
          No active ICP configuration. Fill out the form below to create one.
        </div>
      )}

      <div className="card bg-base-100 border border-base-300 p-4 space-y-4">
        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Vertical</span>
          </label>
          <input
            className="input input-bordered"
            value={vertical}
            onChange={(e) => setVertical(e.target.value)}
            placeholder="e.g. SaaS, FinTech"
            data-testid="input-vertical"
          />
        </div>

        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Target Titles</span>
            <span className="label-text-alt text-base-content/50">comma-separated</span>
          </label>
          <input
            className="input input-bordered"
            value={titles}
            onChange={(e) => setTitles(e.target.value)}
            placeholder="e.g. CTO, VP Engineering"
            data-testid="input-titles"
          />
        </div>

        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Geographies</span>
            <span className="label-text-alt text-base-content/50">comma-separated</span>
          </label>
          <input
            className="input input-bordered"
            value={geographies}
            onChange={(e) => setGeographies(e.target.value)}
            placeholder="e.g. US, EU"
            data-testid="input-geographies"
          />
        </div>

        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Signals</span>
            <span className="label-text-alt text-base-content/50">comma-separated</span>
          </label>
          <input
            className="input input-bordered"
            value={signals}
            onChange={(e) => setSignals(e.target.value)}
            placeholder="e.g. hiring, fundraising"
            data-testid="input-signals"
          />
        </div>

        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Exclusions</span>
            <span className="label-text-alt text-base-content/50">comma-separated</span>
          </label>
          <input
            className="input input-bordered"
            value={exclusions}
            onChange={(e) => setExclusions(e.target.value)}
            placeholder="e.g. government, nonprofit"
            data-testid="input-exclusions"
          />
        </div>

        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Notes</span>
          </label>
          <textarea
            className="textarea textarea-bordered"
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Reviewer notes…"
            data-testid="input-notes"
          />
        </div>

        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Activated by</span>
          </label>
          <input
            className="input input-bordered"
            value={activatedBy}
            onChange={(e) => setActivatedBy(e.target.value)}
            placeholder="Your name or ID"
            data-testid="input-activated-by"
          />
        </div>

        {mutation.isError && (
          <div className="alert alert-error" role="alert" data-testid="save-error">
            {mutation.error instanceof Error
              ? mutation.error.message
              : "Failed to save config"}
          </div>
        )}

        {mutation.isSuccess && (
          <div className="alert alert-success" data-testid="save-success">
            ICP configuration saved.
          </div>
        )}

        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={mutation.isPending}
          data-testid="btn-save-icp"
        >
          {mutation.isPending ? "Saving…" : config ? "Update Config" : "Activate Config"}
        </button>
      </div>
    </div>
  );
}
