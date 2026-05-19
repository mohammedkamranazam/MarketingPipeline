/**
 * Acceptance Criteria:
 * - Loads current client and shows editable name, slug, status fields.
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
import { getClient, updateClient } from "../../services/clientService";
import { ApiError } from "../../services/apiClient";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  status: z.enum(["active", "inactive", "suspended"]),
});

type FormValues = z.infer<typeof schema>;

export function ClientSettingsPage() {
  const { clientId } = useParams<{ clientId: string }>();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["clients", clientId],
    queryFn: () => getClient(clientId!),
    enabled: !!clientId,
  });

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isDirty, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  useEffect(() => {
    if (data) reset({ name: data.name, status: data.status as FormValues["status"] });
  }, [data, reset]);

  const mutation = useMutation({
    mutationFn: (values: FormValues) => updateClient(clientId!, values),
    onSuccess: (updated) => {
      void queryClient.invalidateQueries({ queryKey: ["clients"] });
      reset({ name: updated.name, status: updated.status as FormValues["status"] });
    },
    onError: (err) => {
      if (err instanceof ApiError)
        setError("root", { message: err.message });
    },
  });

  if (isLoading) {
    return <div className="skeleton h-64 w-full" aria-busy="true" aria-label="Loading settings" />;
  }

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-2 mb-6 text-sm text-base-content/60">
        <Link to="/clients">Clients</Link>
        <span>/</span>
        <Link to={`/clients/${clientId}`}>{data?.name}</Link>
        <span>/</span>
        <span>Settings</span>
      </div>
      <h1 className="text-xl font-semibold mb-6">Client settings</h1>

      <form onSubmit={handleSubmit((v) => mutation.mutate(v))} noValidate className="space-y-4">
        {errors.root && (
          <div role="alert" className="alert alert-error text-sm">{errors.root.message}</div>
        )}
        {mutation.isSuccess && (
          <div role="status" className="alert alert-success text-sm">Settings saved.</div>
        )}

        <div className="form-control">
          <label className="label" htmlFor="name"><span className="label-text">Name</span></label>
          <input id="name" className={`input input-bordered w-full ${errors.name ? "input-error" : ""}`} {...register("name")} />
          {errors.name && <span className="label-text-alt text-error mt-1">{errors.name.message}</span>}
        </div>

        <div className="form-control">
          <label className="label" htmlFor="status"><span className="label-text">Status</span></label>
          <select id="status" className="select select-bordered w-full" {...register("status")}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>

        <button type="submit" className="btn btn-primary" disabled={!isDirty || isSubmitting || mutation.isPending}>
          {mutation.isPending && <span className="loading loading-spinner loading-sm" />}
          Save changes
        </button>
      </form>
    </div>
  );
}
