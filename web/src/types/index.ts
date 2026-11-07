export type WarrantStatus =
  | "REQUESTED"
  | "PLANNED"
  | "APPROVED_PLAN"
  | "BUILT"
  | "AUDITED"
  | "APPROVED_MERGE"
  | "OUT_OF_SCOPE"
  | "BLOCKED";

export type ScopeResult = "PENDING" | "CLEAN" | "SCOPE_VIOLATION";
export type AuditorVerdict = "PENDING" | "PASS" | "BLOCK";
export type DataSource = "live" | "seeded";

export interface Warrant {
  id: string;
  room_id: string;
  request_msg_id?: string;
  requester: string;
  plan_md?: string;
  plan_hash?: string;
  approved_by?: string;
  approved_msg_id?: string;
  approved_at?: string;
  branch?: string;
  commit_sha?: string;
  diff_text?: string;
  diff_hash?: string;
  scope_result: ScopeResult;
  offending_files: string[];
  auditor_verdict: AuditorVerdict;
  auditor_notes?: string;
  status: WarrantStatus;
  source: DataSource;
  prev_hash: string;
  record_hash: string;
  created_at: string;
  updated_at: string;
}

export interface WarrantEvent {
  id: string;
  warrant_id: string;
  kind: string;
  actor: string;
  msg_id?: string;
  excerpt: string;
  payload: any;
  at: string;
}

export interface VerificationState {
  computed_plan_hash: string;
  plan_hash_valid: boolean;
  computed_diff_hash: string;
  diff_hash_valid: boolean;
  scope_check: {
    is_clean: boolean;
    scope_result: string;
    planned_files: string[];
    touched_files: string[];
    offending_files: string[];
  };
  computed_record_hash: string;
  stored_record_hash: string;
  is_tampered: boolean;
  is_verified: boolean;
}

export interface WarrantDetailResponse {
  warrant: Warrant;
  events: WarrantEvent[];
  verification: VerificationState;
}

export interface FileProvenanceRecord {
  id: number;
  file_path: string;
  warrant_id: string;
  commit_sha?: string;
  status: string;
  approved_by?: string;
  excerpt?: string;
  at: string;
  requester?: string;
  plan_hash?: string;
  diff_hash?: string;
  scope_result?: string;
}

export interface StatsResponse {
  total: number;
  approved: number;
  out_of_scope: number;
  blocked: number;
  pending: number;
  live_count: number;
  seeded_count: number;
}

export interface SettingsResponse {
  approver_allowlist: string[];
  passphrase_configured: boolean;
  github: {
    is_configured: boolean;
    repo?: string;
    status_message: string;
  };
  switch: {
    server_url: string;
    room_id: string;
  };
  data_sources: {
    live_records: number;
    seeded_records: number;
  };
}
