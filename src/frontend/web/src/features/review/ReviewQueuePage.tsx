/**
 * Acceptance Criteria:
 * - Shows loading, empty, and list states for review items.
 * - Pending items show confidence, item type, content, and evidence.
 * - Clicking an item selects it and shows DecisionToolbar.
 * - DecisionToolbar supports approve, reject, and edit-and-approve actions.
 * - Edit-and-approve shows a text area for edited content (required).
 * - After decision, item is removed from pending queue.
 * - Status filter tabs: all, pending, approved, rejected, edited_and_approved.
 * - No TypeScript `any`.
 */
import { useState } from "react";
import { useParams } from "react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  decideReviewItem,
  listReviewItems,
} from "../../services/reviewService";
import type { ReviewItemResponse } from "../../contracts/review";

type TabStatus = "pending" | "approved" | "rejected" | "edited_and_approved" | "";

const TABS: { label: string; value: TabStatus }[] = [
  { label: "Pending", value: "pending" },
  { label: "Approved", value: "approved" },
  { label: "Rejected", value: "rejected" },
  { label: "Edited", value: "edited_and_approved" },
  { label: "All", value: "" },
];

function confidenceBadge(confidence: number): string {
  if (confidence >= 0.8) return "badge-success";
  if (confidence >= 0.5) return "badge-warning";
  return "badge-error";
}

interface DecisionToolbarProps {
  item: ReviewItemResponse;
  clientId: string;
  pipelineId: string;
  onDone: () => void;
}

function DecisionToolbar({ item, clientId, pipelineId, onDone }: DecisionToolbarProps) {
  const queryClient = useQueryClient();
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState(item.content);
  const [actorNote, setActorNote] = useState("");

  const mutation = useMutation({
    mutationFn: (decision: Parameters<typeof decideReviewItem>[3]) =>
      decideReviewItem(clientId, pipelineId, item.id, decision),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["review-items", clientId, pipelineId] });
      onDone();
    },
  });

  function handleApprove() {
    mutation.mutate({ status: "approved", actor_note: actorNote || undefined });
  }

  function handleReject() {
    mutation.mutate({ status: "rejected", actor_note: actorNote || undefined });
  }

  function handleEditApprove() {
    if (!editedContent.trim()) return;
    mutation.mutate({
      status: "edited_and_approved",
      edited_content: editedContent,
      actor_note: actorNote || undefined,
    });
  }

  return (
    <div className="card bg-base-200 p-4 space-y-3" data-testid="decision-toolbar">
      <div className="space-y-1">
        <p className="font-semibold text-sm">{item.item_type}</p>
        <p className="text-base-content/80">{item.content}</p>
        <p className="text-xs text-base-content/60 italic">{item.evidence_text}</p>
      </div>

      {editMode && (
        <div>
          <label className="label label-text text-xs">Edited content</label>
          <textarea
            className="textarea textarea-bordered w-full"
            rows={3}
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            data-testid="edited-content-input"
          />
        </div>
      )}

      <div>
        <label className="label label-text text-xs">Note (optional)</label>
        <input
          className="input input-bordered input-sm w-full"
          value={actorNote}
          onChange={(e) => setActorNote(e.target.value)}
          placeholder="Reviewer note…"
          data-testid="actor-note-input"
        />
      </div>

      {mutation.isError && (
        <p className="text-error text-sm" role="alert">
          {mutation.error instanceof Error ? mutation.error.message : "Decision failed"}
        </p>
      )}

      <div className="flex gap-2 flex-wrap">
        <button
          className="btn btn-success btn-sm"
          onClick={handleApprove}
          disabled={mutation.isPending || editMode}
          data-testid="btn-approve"
        >
          Approve
        </button>
        <button
          className="btn btn-error btn-sm"
          onClick={handleReject}
          disabled={mutation.isPending || editMode}
          data-testid="btn-reject"
        >
          Reject
        </button>
        {!editMode ? (
          <button
            className="btn btn-warning btn-sm"
            onClick={() => setEditMode(true)}
            disabled={mutation.isPending}
            data-testid="btn-edit-mode"
          >
            Edit &amp; Approve
          </button>
        ) : (
          <>
            <button
              className="btn btn-warning btn-sm"
              onClick={handleEditApprove}
              disabled={mutation.isPending || !editedContent.trim()}
              data-testid="btn-confirm-edit"
            >
              Confirm Edit
            </button>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setEditMode(false)}
              disabled={mutation.isPending}
            >
              Cancel
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export function ReviewQueuePage() {
  const { clientId = "", pipelineId = "" } = useParams();
  const [activeTab, setActiveTab] = useState<TabStatus>("pending");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: items, isLoading, error } = useQuery({
    queryKey: ["review-items", clientId, pipelineId, activeTab],
    queryFn: () => listReviewItems(clientId, pipelineId, activeTab || undefined),
    enabled: Boolean(clientId && pipelineId),
  });

  const selectedItem = items?.find((i) => i.id === selectedId) ?? null;

  function handleTabChange(tab: TabStatus) {
    setActiveTab(tab);
    setSelectedId(null);
  }

  if (isLoading) return <div className="p-4"><span className="loading loading-spinner" /></div>;
  if (error) return (
    <div className="p-4 text-error" role="alert">
      Failed to load review items: {error instanceof Error ? error.message : "Unknown error"}
    </div>
  );

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold">Review Queue</h1>

      <div role="tablist" className="tabs tabs-boxed w-fit">
        {TABS.map((tab) => (
          <button
            key={tab.value}
            role="tab"
            className={`tab${activeTab === tab.value ? " tab-active" : ""}`}
            onClick={() => handleTabChange(tab.value)}
            data-testid={`tab-${tab.value || "all"}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {items && items.length === 0 && (
        <p className="text-base-content/60" data-testid="empty-state">
          No items in this queue.
        </p>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ul className="space-y-2" data-testid="review-item-list">
          {items?.map((item) => (
            <li key={item.id}>
              <button
                className={`card w-full text-left bg-base-100 border cursor-pointer p-3 hover:bg-base-200 transition-colors${
                  selectedId === item.id ? " border-primary" : " border-base-300"
                }`}
                onClick={() => setSelectedId(item.id)}
                data-testid={`review-item-${item.id}`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-medium text-sm">{item.item_type}</span>
                  <span
                    className={`badge badge-sm ${confidenceBadge(item.confidence)}`}
                  >
                    {Math.round(item.confidence * 100)}%
                  </span>
                </div>
                <p className="text-sm truncate">{item.content}</p>
                <p className="text-xs text-base-content/50 mt-1 truncate">{item.evidence_text}</p>
              </button>
            </li>
          ))}
        </ul>

        {selectedItem && selectedItem.status === "pending" && (
          <DecisionToolbar
            item={selectedItem}
            clientId={clientId}
            pipelineId={pipelineId}
            onDone={() => setSelectedId(null)}
          />
        )}

        {selectedItem && selectedItem.status !== "pending" && (
          <div className="card bg-base-100 border border-base-300 p-4 space-y-2" data-testid="decided-item-detail">
            <p className="font-semibold text-sm">{selectedItem.item_type}</p>
            <p>{selectedItem.content}</p>
            {selectedItem.edited_content && (
              <div>
                <p className="text-xs text-base-content/60">Edited to:</p>
                <p className="italic">{selectedItem.edited_content}</p>
              </div>
            )}
            <p className="text-xs text-base-content/50">
              {selectedItem.status} by {selectedItem.actor_id ?? "unknown"}{" "}
              {selectedItem.decided_at ? `at ${selectedItem.decided_at}` : ""}
            </p>
            {selectedItem.actor_note && (
              <p className="text-xs italic text-base-content/60">{selectedItem.actor_note}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
