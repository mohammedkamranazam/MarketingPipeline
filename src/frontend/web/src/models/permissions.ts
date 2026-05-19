/**
 * Acceptance Criteria:
 * - Five personas: admin, domain_expert, reviewer, sales_operator, compliance_reviewer.
 * - canApproveReviewItem, canEditReviewItem, canRejectReviewItem require domain_expert or admin.
 * - canManageGuardrails requires domain_expert or compliance_reviewer or admin.
 * - canManageSuppressionRules requires compliance_reviewer or admin.
 * - canViewICPConfig is available to all roles.
 * - canActivateICPConfig requires domain_expert or admin.
 * - canManageUsers requires admin.
 * - No TypeScript `any`.
 */

export type UserRole =
  | "admin"
  | "domain_expert"
  | "reviewer"
  | "sales_operator"
  | "compliance_reviewer";

export interface Permission {
  canApproveReviewItem: boolean;
  canEditReviewItem: boolean;
  canRejectReviewItem: boolean;
  canActivateICPConfig: boolean;
  canViewICPConfig: boolean;
  canManageGuardrails: boolean;
  canManageSuppressionRules: boolean;
  canViewAuditLog: boolean;
  canManageUsers: boolean;
  canViewOutreachGuardrails: boolean;
}

const PERMISSION_MAP: Record<UserRole, Permission> = {
  admin: {
    canApproveReviewItem: true,
    canEditReviewItem: true,
    canRejectReviewItem: true,
    canActivateICPConfig: true,
    canViewICPConfig: true,
    canManageGuardrails: true,
    canManageSuppressionRules: true,
    canViewAuditLog: true,
    canManageUsers: true,
    canViewOutreachGuardrails: true,
  },
  domain_expert: {
    canApproveReviewItem: true,
    canEditReviewItem: true,
    canRejectReviewItem: true,
    canActivateICPConfig: true,
    canViewICPConfig: true,
    canManageGuardrails: true,
    canManageSuppressionRules: false,
    canViewAuditLog: true,
    canManageUsers: false,
    canViewOutreachGuardrails: true,
  },
  reviewer: {
    canApproveReviewItem: false,
    canEditReviewItem: false,
    canRejectReviewItem: false,
    canActivateICPConfig: false,
    canViewICPConfig: true,
    canManageGuardrails: false,
    canManageSuppressionRules: false,
    canViewAuditLog: true,
    canManageUsers: false,
    canViewOutreachGuardrails: false,
  },
  sales_operator: {
    canApproveReviewItem: false,
    canEditReviewItem: false,
    canRejectReviewItem: false,
    canActivateICPConfig: false,
    canViewICPConfig: true,
    canManageGuardrails: false,
    canManageSuppressionRules: false,
    canViewAuditLog: false,
    canManageUsers: false,
    canViewOutreachGuardrails: true,
  },
  compliance_reviewer: {
    canApproveReviewItem: false,
    canEditReviewItem: false,
    canRejectReviewItem: false,
    canActivateICPConfig: false,
    canViewICPConfig: true,
    canManageGuardrails: true,
    canManageSuppressionRules: true,
    canViewAuditLog: true,
    canManageUsers: false,
    canViewOutreachGuardrails: true,
  },
};

export function getPermissions(role: UserRole): Permission {
  return PERMISSION_MAP[role];
}
