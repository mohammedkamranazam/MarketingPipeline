/**
 * Acceptance Criteria:
 * - Form requires name, slug, and lane fields.
 * - Slug is auto-suggested from name.
 * - Validates all required fields before submit.
 * - Maps server errors to the form root.
 * - On success navigates to the pipeline detail page.
 * - No TypeScript `any`.
 */
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams, Link } from "react-router";
import { createPipeline, getClient } from "../../services/clientService";
import { ApiError } from "../../services/apiClient";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  slug: z
    .string()
    .min(1, "Slug is required")
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "Slug must be lowercase-hyphenated"),
  lane: z.enum(["discovery", "seed_enrichment"]),
  description: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

function toSlug(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export function PipelineCreatePage() {
  const { clientId } = useParams<{ clientId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: client } = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => getClient(clientId!),
    enabled: !!clientId,
  });

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { lane: "discovery" },
  });

  const mutation = useMutation({
    mutationFn: (values: FormValues) => createPipeline(clientId!, values),
    onSuccess: (pipeline) => {
      void queryClient.invalidateQueries({ queryKey: ["clients", clientId, "pipelines"] });
      void navigate(`/clients/${clientId}/pipelines/${pipeline.id}`);
    },
    onError: (err) => {
      if (err instanceof ApiError) setError("root", { message: err.message });
    },
  });

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-2 mb-6 text-sm text-base-content/60">
        <Link to="/clients">Clients</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}`}>{client?.name ?? clientId}</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}/pipelines`}>Pipelines</Link>
        <span>/</span>
        <span>New</span>
      </div>
      <h1 className="text-xl font-semibold mb-6">New pipeline</h1>

      <form onSubmit={handleSubmit((v) => mutation.mutate(v))} noValidate className="space-y-4">
        {errors.root && (
          <div role="alert" className="alert alert-error text-sm">{errors.root.message}</div>
        )}

        <div className="form-control">
          <label className="label" htmlFor="p-name"><span className="label-text">Name</span></label>
          <input
            id="p-name"
            className={`input input-bordered w-full ${errors.name ? "input-error" : ""}`}
            {...register("name", {
              onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
                setValue("slug", toSlug(e.target.value), { shouldValidate: false }),
            })}
          />
          {errors.name && <span className="label-text-alt text-error mt-1">{errors.name.message}</span>}
        </div>

        <div className="form-control">
          <label className="label" htmlFor="p-slug"><span className="label-text">Slug</span></label>
          <input
            id="p-slug"
            className={`input input-bordered w-full font-mono text-sm ${errors.slug ? "input-error" : ""}`}
            {...register("slug")}
          />
          {errors.slug && <span className="label-text-alt text-error mt-1">{errors.slug.message}</span>}
        </div>

        <div className="form-control">
          <label className="label" htmlFor="p-lane"><span className="label-text">Lane</span></label>
          <select id="p-lane" className="select select-bordered w-full" {...register("lane")}>
            <option value="discovery">Discovery</option>
            <option value="seed_enrichment">Seed Enrichment</option>
          </select>
        </div>

        <div className="form-control">
          <label className="label" htmlFor="p-description"><span className="label-text">Description</span></label>
          <textarea id="p-description" className="textarea textarea-bordered w-full" rows={2} {...register("description")} />
        </div>

        <div className="flex gap-3 pt-2">
          <button type="submit" className="btn btn-primary" disabled={isSubmitting || mutation.isPending}>
            {mutation.isPending && <span className="loading loading-spinner loading-sm" />}
            Create pipeline
          </button>
          <Link to={`/clients/${clientId}/pipelines`} className="btn btn-ghost">Cancel</Link>
        </div>
      </form>
    </div>
  );
}
