/**
 * Acceptance Criteria:
 * - Form has name and slug fields; both are required.
 * - Slug is auto-suggested from name (lowercase, hyphens).
 * - Validates required fields before submit and shows inline errors.
 * - Maps server validation errors to fields when available.
 * - On success, navigates to the created client detail page.
 * - No TypeScript `any`.
 */
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate, Link } from "react-router";
import { createClient } from "../../services/clientService";
import { ApiError } from "../../services/apiClient";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  slug: z
    .string()
    .min(1, "Slug is required")
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "Slug must be lowercase-hyphenated"),
  status: z.enum(["active", "inactive", "suspended"]),
});

type FormValues = z.infer<typeof schema>;

function toSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function ClientCreatePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { status: "active" },
  });

  const mutation = useMutation({
    mutationFn: createClient,
    onSuccess: (client) => {
      void queryClient.invalidateQueries({ queryKey: ["clients"] });
      void navigate(`/clients/${client.id}`);
    },
    onError: (err) => {
      if (err instanceof ApiError) {
        setError("root", { message: err.message });
      }
    },
  });

  function onSubmit(values: FormValues) {
    mutation.mutate(values);
  }

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-2 mb-6 text-sm text-base-content/60">
        <Link to="/clients">Clients</Link>
        <span>/</span>
        <span>New</span>
      </div>
      <h1 className="text-xl font-semibold mb-6">New client</h1>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        {errors.root && (
          <div role="alert" className="alert alert-error text-sm">
            {errors.root.message}
          </div>
        )}

        <div className="form-control">
          <label className="label" htmlFor="name">
            <span className="label-text">Name</span>
          </label>
          <input
            id="name"
            className={`input input-bordered w-full ${errors.name ? "input-error" : ""}`}
            {...register("name", {
              onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
                setValue("slug", toSlug(e.target.value), {
                  shouldValidate: false,
                });
              },
            })}
          />
          {errors.name && (
            <span className="label-text-alt text-error mt-1">
              {errors.name.message}
            </span>
          )}
        </div>

        <div className="form-control">
          <label className="label" htmlFor="slug">
            <span className="label-text">Slug</span>
          </label>
          <input
            id="slug"
            className={`input input-bordered w-full font-mono text-sm ${errors.slug ? "input-error" : ""}`}
            {...register("slug")}
          />
          {errors.slug && (
            <span className="label-text-alt text-error mt-1">
              {errors.slug.message}
            </span>
          )}
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isSubmitting || mutation.isPending}
          >
            {mutation.isPending && (
              <span className="loading loading-spinner loading-sm" />
            )}
            Create client
          </button>
          <Link to="/clients" className="btn btn-ghost">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
