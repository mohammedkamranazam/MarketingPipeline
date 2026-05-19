/**
 * Acceptance Criteria:
 * - Lists all credential profiles for the pipeline.
 * - Shows status badge (active/expiring/expired/validation_failed/etc).
 * - Shows masked_fingerprint (never raw secrets).
 * - Shows expires_at, last_validated_at, next_validation_at, rotation_due_at when present.
 * - "Validate" button triggers validation and refreshes profile status.
 * - Shows validation run result (passed/failed) after trigger.
 * - "Add Credential" navigates to create form.
 * - No TypeScript `any`.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import type { CredentialValidationRunResponse } from "../../contracts/source";
import { listCredentialProfiles, validateCredential } from "../../services/sourceService";

export function CredentialHealthPage() {
  const { clientId, pipelineId } = useParams<{
    clientId: string;
    pipelineId: string;
  }>();
  const qc = useQueryClient();
  const [lastRuns, setLastRuns] = useState<Record<string, CredentialValidationRunResponse>>({});

  const { data: profiles, isLoading, isError } = useQuery({
    queryKey: ["credentials", clientId, pipelineId],
    queryFn: () => listCredentialProfiles(clientId!, pipelineId!),
    enabled: Boolean(clientId && pipelineId),
  });

  const validateMutation = useMutation({
    mutationFn: (profileId: string) =>
      validateCredential(clientId!, pipelineId!, profileId),
    onSuccess: (run) => {
      setLastRuns((prev) => ({ ...prev, [run.credential_profile_id]: run }));
      void qc.invalidateQueries({ queryKey: ["credentials", clientId, pipelineId] });
    },
  });

  const base = `/clients/${clientId}/pipelines/${pipelineId}`;

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="skeleton h-8 w-48 mb-4" />
        <div className="skeleton h-32 w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-6">
        <div className="alert alert-error">
          <span>Failed to load credential profiles.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Credential Health</h1>
        <Link to={`${base}/credentials/new`} className="btn btn-primary btn-sm">
          Add Credential
        </Link>
      </div>

      {profiles?.length === 0 ? (
        <div className="text-center py-12 text-base-content/50">
          No credentials configured.
        </div>
      ) : (
        <div className="space-y-4">
          {profiles?.map((profile) => {
            const lastRun = lastRuns[profile.id];
            return (
              <div key={profile.id} className="card bg-base-200 shadow-sm">
                <div className="card-body p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{profile.name}</h3>
                        <CredentialStatusBadge status={profile.status} />
                      </div>
                      <p className="text-sm text-base-content/60">
                        Adapter: <code>{profile.adapter_key}</code>
                      </p>
                      {profile.masked_fingerprint && (
                        <p className="text-sm font-mono text-base-content/60">
                          Fingerprint: {profile.masked_fingerprint}
                        </p>
                      )}
                      <div className="text-xs text-base-content/50 space-y-0.5 mt-1">
                        {profile.expires_at && (
                          <p>Expires: {formatDate(profile.expires_at)}</p>
                        )}
                        {profile.last_validated_at && (
                          <p>Last validated: {formatDate(profile.last_validated_at)}</p>
                        )}
                        {profile.next_validation_at && (
                          <p>Next validation: {formatDate(profile.next_validation_at)}</p>
                        )}
                        {profile.rotation_due_at && (
                          <p className="text-warning">
                            Rotation due: {formatDate(profile.rotation_due_at)}
                          </p>
                        )}
                        {profile.scopes.length > 0 && (
                          <p>Scopes: {profile.scopes.join(", ")}</p>
                        )}
                      </div>
                    </div>
                    <button
                      className="btn btn-sm btn-outline"
                      disabled={validateMutation.isPending}
                      onClick={() => validateMutation.mutate(profile.id)}
                    >
                      {validateMutation.isPending &&
                      validateMutation.variables === profile.id ? (
                        <span className="loading loading-spinner loading-xs" />
                      ) : (
                        "Validate"
                      )}
                    </button>
                  </div>

                  {lastRun && (
                    <div
                      className={`alert alert-sm mt-2 ${
                        lastRun.status === "passed" ? "alert-success" : "alert-error"
                      }`}
                    >
                      <span className="text-sm">
                        Validation {lastRun.status}
                        {lastRun.reason ? `: ${lastRun.reason}` : ""}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function CredentialStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: "badge-success",
    expiring: "badge-warning",
    expired: "badge-error",
    validation_failed: "badge-error",
    insufficient_scope: "badge-warning",
    revoked: "badge-error",
    disabled: "badge-ghost",
  };
  return (
    <span className={`badge badge-sm ${colors[status] ?? "badge-ghost"}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
