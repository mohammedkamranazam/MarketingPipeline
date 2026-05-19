/**
 * Acceptance Criteria:
 * - Displays existing policy rules ordered by priority.
 * - Provides a URL input to test policy decisions.
 * - Submitting a URL shows the policy decision result (allow/block/review).
 * - Shows matched_rule_id when a rule matched.
 * - Shows loading state during decision fetch.
 * - Shows error state when decision fetch fails.
 * - "Add Rule" form creates new policy rules.
 * - Deleting a rule removes it from the list.
 * - No TypeScript `any`.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import type { PolicyDecisionResponse, PolicyRuleCreate } from "../../contracts/source";
import {
  createPolicyRule,
  decidePolicy,
  deletePolicyRule,
  listPolicyRules,
} from "../../services/sourceService";

export function PolicySimulatorPage() {
  const { clientId, pipelineId } = useParams<{
    clientId: string;
    pipelineId: string;
  }>();
  const qc = useQueryClient();
  const [testUrl, setTestUrl] = useState("");
  const [decision, setDecision] = useState<PolicyDecisionResponse | null>(null);
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newPattern, setNewPattern] = useState("");
  const [newDecision, setNewDecision] = useState<"allow" | "block" | "review">("allow");

  const { data: rules, isLoading, isError } = useQuery({
    queryKey: ["policy-rules", clientId, pipelineId],
    queryFn: () => listPolicyRules(clientId!, pipelineId!),
    enabled: Boolean(clientId && pipelineId),
  });

  const decideMutation = useMutation({
    mutationFn: () =>
      decidePolicy(clientId!, pipelineId!, {
        operation_type: "fetch",
        url: testUrl,
      }),
    onSuccess: (result) => {
      setDecision(result);
      setDecisionError(null);
    },
    onError: () => setDecisionError("Failed to evaluate policy."),
  });

  const addRuleMutation = useMutation({
    mutationFn: (payload: PolicyRuleCreate) =>
      createPolicyRule(clientId!, pipelineId!, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["policy-rules", clientId, pipelineId] });
      setShowAddForm(false);
      setNewPattern("");
      setNewDecision("allow");
    },
  });

  const deleteRuleMutation = useMutation({
    mutationFn: (ruleId: string) =>
      deletePolicyRule(clientId!, pipelineId!, ruleId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["policy-rules", clientId, pipelineId] });
    },
  });

  const decisionColor: Record<string, string> = {
    allow: "alert-success",
    block: "alert-error",
    review: "alert-warning",
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Policy Simulator</h1>

      {/* URL tester */}
      <div className="card bg-base-200 p-4 space-y-3">
        <h2 className="font-semibold text-lg">Test a URL</h2>
        <div className="flex gap-2">
          <input
            type="url"
            className="input input-bordered flex-1"
            placeholder="https://example.com/page"
            value={testUrl}
            onChange={(e) => setTestUrl(e.target.value)}
          />
          <button
            className="btn btn-primary"
            disabled={!testUrl || decideMutation.isPending}
            onClick={() => decideMutation.mutate()}
          >
            {decideMutation.isPending ? (
              <span className="loading loading-spinner loading-sm" />
            ) : (
              "Evaluate"
            )}
          </button>
        </div>
        {decisionError && (
          <div className="alert alert-error">
            <span>{decisionError}</span>
          </div>
        )}
        {decision && (
          <div className={`alert ${decisionColor[decision.decision] ?? "alert-info"}`}>
            <div>
              <p className="font-bold capitalize">{decision.decision}</p>
              {decision.matched_rule_id && (
                <p className="text-sm">Matched rule: {decision.matched_rule_id}</p>
              )}
              {!decision.matched_rule_id && (
                <p className="text-sm">No rule matched — using default.</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Rules list */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-lg">Policy Rules</h2>
          <button
            className="btn btn-sm btn-outline"
            onClick={() => setShowAddForm((v) => !v)}
          >
            {showAddForm ? "Cancel" : "Add Rule"}
          </button>
        </div>

        {showAddForm && (
          <div className="card bg-base-200 p-4 space-y-3">
            <input
              type="text"
              className="input input-bordered w-full"
              placeholder="URL pattern (e.g. https://blocked.com)"
              value={newPattern}
              onChange={(e) => setNewPattern(e.target.value)}
            />
            <select
              className="select select-bordered w-full"
              value={newDecision}
              onChange={(e) =>
                setNewDecision(e.target.value as "allow" | "block" | "review")
              }
            >
              <option value="allow">Allow</option>
              <option value="block">Block</option>
              <option value="review">Review</option>
            </select>
            <button
              className="btn btn-primary btn-sm"
              disabled={!newPattern || addRuleMutation.isPending}
              onClick={() =>
                addRuleMutation.mutate({
                  entity_type: "url_pattern",
                  pattern: newPattern,
                  decision: newDecision,
                })
              }
            >
              Save Rule
            </button>
          </div>
        )}

        {isLoading && <div className="skeleton h-20 w-full" />}
        {isError && (
          <div className="alert alert-error">
            <span>Failed to load policy rules.</span>
          </div>
        )}
        {rules?.length === 0 && !isLoading && (
          <p className="text-base-content/50 text-sm">No policy rules defined.</p>
        )}
        {rules?.map((rule) => (
          <div key={rule.id} className="card bg-base-200 p-3 flex flex-row items-center gap-4">
            <div className="flex-1">
              <span className="font-mono text-sm">{rule.pattern ?? rule.entity_id}</span>
              <span className="ml-2 text-xs text-base-content/60">
                priority {rule.priority}
              </span>
            </div>
            <DecisionBadge decision={rule.decision} />
            <button
              className="btn btn-ghost btn-xs text-error"
              onClick={() => deleteRuleMutation.mutate(rule.id)}
              disabled={deleteRuleMutation.isPending}
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function DecisionBadge({ decision }: { decision: string }) {
  const colors: Record<string, string> = {
    allow: "badge-success",
    block: "badge-error",
    review: "badge-warning",
  };
  return (
    <span className={`badge ${colors[decision] ?? "badge-ghost"}`}>{decision}</span>
  );
}
