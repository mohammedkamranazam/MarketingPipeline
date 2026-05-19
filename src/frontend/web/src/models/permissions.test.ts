/**
 * Tests for the permissions model (P03-FE01).
 *
 * Acceptance criteria tested:
 * - admin has all permissions.
 * - domain_expert can approve, edit, reject, and activate ICP config.
 * - domain_expert cannot manage suppression rules.
 * - reviewer cannot approve, edit, or reject items.
 * - reviewer can view ICP config.
 * - sales_operator can only view outreach guardrails and ICP config.
 * - sales_operator cannot manage anything.
 * - compliance_reviewer can manage suppression rules and guardrails.
 * - compliance_reviewer cannot approve or reject review items.
 * - compliance_reviewer cannot manage users.
 */
import { describe, expect, it } from "vitest";
import { getPermissions } from "./permissions";

describe("admin permissions", () => {
  const p = getPermissions("admin");

  it("can approve review items", () => expect(p.canApproveReviewItem).toBe(true));
  it("can edit review items", () => expect(p.canEditReviewItem).toBe(true));
  it("can reject review items", () => expect(p.canRejectReviewItem).toBe(true));
  it("can activate ICP config", () => expect(p.canActivateICPConfig).toBe(true));
  it("can manage guardrails", () => expect(p.canManageGuardrails).toBe(true));
  it("can manage suppression rules", () => expect(p.canManageSuppressionRules).toBe(true));
  it("can manage users", () => expect(p.canManageUsers).toBe(true));
  it("can view audit log", () => expect(p.canViewAuditLog).toBe(true));
});

describe("domain_expert permissions", () => {
  const p = getPermissions("domain_expert");

  it("can approve review items", () => expect(p.canApproveReviewItem).toBe(true));
  it("can edit review items", () => expect(p.canEditReviewItem).toBe(true));
  it("can reject review items", () => expect(p.canRejectReviewItem).toBe(true));
  it("can activate ICP config", () => expect(p.canActivateICPConfig).toBe(true));
  it("can manage guardrails", () => expect(p.canManageGuardrails).toBe(true));
  it("cannot manage suppression rules", () => expect(p.canManageSuppressionRules).toBe(false));
  it("cannot manage users", () => expect(p.canManageUsers).toBe(false));
});

describe("reviewer permissions", () => {
  const p = getPermissions("reviewer");

  it("cannot approve review items", () => expect(p.canApproveReviewItem).toBe(false));
  it("cannot edit review items", () => expect(p.canEditReviewItem).toBe(false));
  it("cannot reject review items", () => expect(p.canRejectReviewItem).toBe(false));
  it("cannot activate ICP config", () => expect(p.canActivateICPConfig).toBe(false));
  it("can view ICP config", () => expect(p.canViewICPConfig).toBe(true));
  it("cannot manage guardrails", () => expect(p.canManageGuardrails).toBe(false));
  it("cannot manage suppression rules", () => expect(p.canManageSuppressionRules).toBe(false));
  it("cannot manage users", () => expect(p.canManageUsers).toBe(false));
});

describe("sales_operator permissions", () => {
  const p = getPermissions("sales_operator");

  it("cannot approve review items", () => expect(p.canApproveReviewItem).toBe(false));
  it("can view ICP config", () => expect(p.canViewICPConfig).toBe(true));
  it("can view outreach guardrails", () => expect(p.canViewOutreachGuardrails).toBe(true));
  it("cannot manage guardrails", () => expect(p.canManageGuardrails).toBe(false));
  it("cannot manage suppression rules", () => expect(p.canManageSuppressionRules).toBe(false));
  it("cannot view audit log", () => expect(p.canViewAuditLog).toBe(false));
  it("cannot manage users", () => expect(p.canManageUsers).toBe(false));
});

describe("compliance_reviewer permissions", () => {
  const p = getPermissions("compliance_reviewer");

  it("cannot approve review items", () => expect(p.canApproveReviewItem).toBe(false));
  it("cannot edit review items", () => expect(p.canEditReviewItem).toBe(false));
  it("cannot reject review items", () => expect(p.canRejectReviewItem).toBe(false));
  it("cannot activate ICP config", () => expect(p.canActivateICPConfig).toBe(false));
  it("can view ICP config", () => expect(p.canViewICPConfig).toBe(true));
  it("can manage guardrails", () => expect(p.canManageGuardrails).toBe(true));
  it("can manage suppression rules", () => expect(p.canManageSuppressionRules).toBe(true));
  it("can view audit log", () => expect(p.canViewAuditLog).toBe(true));
  it("cannot manage users", () => expect(p.canManageUsers).toBe(false));
});
