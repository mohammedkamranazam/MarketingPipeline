/**
 * Acceptance Criteria:
 * - Loads pipeline and shows editable name, lane, status, description fields.
 * - Dirty-state guard: submit button enabled only when form has changes.
 * - Saves via PATCH and shows success/error feedback.
 * - No TypeScript `any`.
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, Link } from "react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useEffect } from "react";
import { getPipeline, getClient, updatePipeline } from "../../services/clientService";
import { ApiError } from "../../services/apiClient";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  lane: z.enum(["discovery", "seed_enrichment"]),
  status: z.enum(["active", "paused", "archived"]),
  description: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function PipelineSettingsPage() {
  const { clientId, pipelineId } = useParams<{ clientId: string; pipelineId: string }>();
  const queryClient = useQueryClient();

  const clientQuery = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => getClient(clientId!),
    enabled: !!clientId,
  });

  const pipelineQuery = useQuery({
    queryKey: ["clients", clientId, "pipelines", pipelineId],
    queryFn: () => getPipeline(clientId!, pipelineId!),
    enabled: !!clientId && !!pipelineId,
  });

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isDirty, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const pipeline = pipelineQuery.data;

  useEffect(() => {
    if (pipeline) {
      reset({
        name: pipeline.name,
        lane: pipeline.lane,
        status: pipeline.status as FormValues["status"],
        description: pipeline.description ?? "",
      });
    }
  }, [pipeline, reset]);

  const mutation = useMutation({
    mutationFn: (values: FormValues) => updatePipeline(clientId!, pipelineId!, values),
    onSuccess: (updated) => {
      void queryClient.invalidateQueries({ queryKey: ["clients", clientId, "pipelines"] });
      reset({
        name: updated.name,
        lane: updated.lane,
        status: updated.status as FormValues["status"],
        description: updated.description ?? "",
      });
    },
    onError: (err) => {
      if (err instanceof ApiError) setError("root", { message: err.message });
    },
  });

  if (pipelineQuery.isLoading) {
    return <div className="skeleton h-64 w-full" aria-busy="true" aria-label="Loading pipeline settings" />;
  }

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-2 mb-6 text-sm text-base-content/60">
        <Link to="/clients">Clients</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}`}>{clientQuery.data?.name ?? clientId}</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}/pipelines`}>Pipelines</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}/pipelines/${pipelineId}`}>{pipeline?.name}</Link>
        <span>/</span>
        <span>Settings</span>
      </div>
      <h1 className="text-xl font-semibold mb-6">Pipeline settings</h1>

      <form onSubmit={handleSubmit((v) => mutation.mutate(v))} noValidate className="space-y-4">
        {errors.root && (
          <div role="alert" className="alert alert-error text-sm">{errors.root.message}</div>
        )}
        {mutation.isSuccess && (
          <div role="status" className="alert alert-success text-sm">Settings saved.</div>
        )}

        <div className="form-control">
          <label className="label" htmlFor="ps-name"><span className="label-text">Name</span></label>
          <input id="ps-name" className={`input input-bordered w-full ${errors.name ? "input-error" : ""}`} {...register("name")} />
          {errors.name && <span className="label-text-alt text-error mt-1">{errors.name.message}</span>}
        </div>

        <div className="form-control">
          <label className="label" htmlFor="ps-lane"><span className="label-text">Lane</span></label>
          <select id="ps-lane" className="select select-bordered w-full" {...register("lane")}>
            <option value="discovery">Discovery</option>
            <option value="seed_enrichment">Seed Enrichment</option>
          </select>
        </div>

        <div className="form-control">
          <label className="label" htmlFor="ps-status"><span className="label-text">Status</span></label>
          <select id="ps-status" className="select select-bordered w-full" {...register("status")}>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="archived">Archived</option>
          </select>
        </div>

        <div className="form-control">
          <label className="label" htmlFor="ps-desc"><span className="label-text">Description</span></label>
          <textarea id="ps-desc" className="textarea textarea-bordered w-full" rows={2} {...register("description")} />
        </div>

        <button type="submit" className="btn btn-primary" disabled={!isDirty || isSubmitting || mutation.isPending}>
          {mutation.isPending && <span className="loading loading-spinner loading-sm" />}
          Save changes
        </button>
      </form>
    </div>
  );
}
