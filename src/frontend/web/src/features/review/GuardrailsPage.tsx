/**
 * Acceptance Criteria:
 * - Lists all enrichment guardrails with enabled/disabled status.
 * - Toggle enables or disables a guardrail via PUT /guardrails.
 * - Shows policy impact: outreach export blocked when outreach_export guardrail is disabled.
 * - Shows approved_by and approved_at for enabled guardrails.
 * - Shows loading and error states.
 * - No TypeScript `any`.
 */
import { useParams } from "react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listGuardrails, upsertGuardrail } from "../../services/reviewService";
import type { EnrichmentGuardrailResponse } from "../../contracts/review";

const GUARDRAIL_LABELS: Record<string, string> = {
  enrichment_provider: "Enrichment Provider",
  email_verification: "Email Verification",
  outreach_export: "Outreach Export",
};

const GUARDRAIL_IMPACT: Record<string, string> = {
  enrichment_provider: "Profile enrichment will be disabled until this is enabled.",
  email_verification: "Email verification will be skipped, affecting contact quality.",
  outreach_export: "No contacts can be exported for outreach until this is enabled.",
};

interface GuardrailRowProps {
  guardrail: EnrichmentGuardrailResponse;
  clientId: string;
  pipelineId: string;
}

function GuardrailRow({ guardrail, clientId, pipelineId }: GuardrailRowProps) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (enabled: boolean) =>
      upsertGuardrail(clientId, pipelineId, {
        guardrail_type: guardrail.guardrail_type as
          | "enrichment_provider"
          | "email_verification"
          | "outreach_export",
        enabled,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["guardrails", clientId, pipelineId] });
    },
  });

  const label = GUARDRAIL_LABELS[guardrail.guardrail_type] ?? guardrail.guardrail_type;
  const impact = GUARDRAIL_IMPACT[guardrail.guardrail_type];

  return (
    <div
      className="card bg-base-100 border border-base-300 p-4 space-y-2"
      data-testid={`guardrail-${guardrail.guardrail_type}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium">{label}</p>
          {!guardrail.enabled && impact && (
            <p className="text-xs text-warning mt-0.5" data-testid="policy-impact">
              {impact}
            </p>
          )}
        </div>
        <input
          type="checkbox"
          className="toggle toggle-success"
          checked={guardrail.enabled}
          disabled={mutation.isPending}
          onChange={(e) => mutation.mutate(e.target.checked)}
          data-testid={`toggle-${guardrail.guardrail_type}`}
          aria-label={`Toggle ${label}`}
        />
      </div>

      {guardrail.enabled && guardrail.approved_by && (
        <p className="text-xs text-base-content/50">
          Approved by {guardrail.approved_by}
          {guardrail.approved_at ? ` at ${guardrail.approved_at}` : ""}
        </p>
      )}

      {guardrail.policy_notes && (
        <p className="text-xs italic text-base-content/60">{guardrail.policy_notes}</p>
      )}

      {mutation.isError && (
        <p className="text-error text-xs" role="alert">
          {mutation.error instanceof Error ? mutation.error.message : "Failed to update guardrail"}
        </p>
      )}
    </div>
  );
}

export function GuardrailsPage() {
  const { clientId = "", pipelineId = "" } = useParams();

  const { data: guardrails, isLoading, error } = useQuery({
    queryKey: ["guardrails", clientId, pipelineId],
    queryFn: () => listGuardrails(clientId, pipelineId),
    enabled: Boolean(clientId && pipelineId),
  });

  if (isLoading) return <div className="p-4"><span className="loading loading-spinner" /></div>;
  if (error) return (
    <div className="p-4 text-error" role="alert">
      Failed to load guardrails: {error instanceof Error ? error.message : "Unknown error"}
    </div>
  );

  return (
    <div className="p-4 space-y-4 max-w-2xl">
      <h1 className="text-xl font-bold">Enrichment Guardrails</h1>

      {guardrails && guardrails.length === 0 && (
        <p className="text-base-content/60" data-testid="no-guardrails">
          No guardrails configured for this pipeline.
        </p>
      )}

      <div className="space-y-3" data-testid="guardrail-list">
        {guardrails?.map((g) => (
          <GuardrailRow
            key={g.id}
            guardrail={g}
            clientId={clientId}
            pipelineId={pipelineId}
          />
        ))}
      </div>
    </div>
  );
}
