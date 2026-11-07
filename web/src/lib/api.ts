import {
  FileProvenanceRecord,
  SettingsResponse,
  StatsResponse,
  Warrant,
  WarrantDetailResponse,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_CLERK_API_URL || "http://127.0.0.1:8000";

export async function fetchWarrants(
  source?: string,
  status?: string
): Promise<Warrant[]> {
  try {
    const params = new URLSearchParams();
    if (source) params.append("source", source);
    if (status) params.append("status", status);
    const query = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${BASE_URL}/api/warrants${query}`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("Failed to fetch warrants from Clerk API:", err);
    return [];
  }
}

export async function fetchWarrant(
  id: string
): Promise<WarrantDetailResponse | null> {
  try {
    const res = await fetch(`${BASE_URL}/api/warrants/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn(`Failed to fetch warrant ${id}:`, err);
    return null;
  }
}

export async function fetchFileProvenance(
  filePath: string
): Promise<FileProvenanceRecord[]> {
  try {
    const res = await fetch(`${BASE_URL}/api/files/${encodeURIComponent(filePath)}/provenance`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.records || [];
  } catch (err) {
    console.warn(`Failed to fetch provenance for ${filePath}:`, err);
    return [];
  }
}

export async function fetchVerification(sha: string): Promise<any> {
  try {
    const res = await fetch(`${BASE_URL}/api/verify/${sha}`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      commit_sha: sha,
      verified: false,
      status: "UNAUTHORIZED",
      reason: "Could not connect to Warrant Clerk verification service.",
    };
  }
}

export async function fetchStats(): Promise<StatsResponse> {
  try {
    const res = await fetch(`${BASE_URL}/api/stats`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      total: 0,
      approved: 0,
      out_of_scope: 0,
      blocked: 0,
      pending: 0,
      live_count: 0,
      seeded_count: 0,
    };
  }
}

export async function fetchSettings(): Promise<SettingsResponse> {
  try {
    const res = await fetch(`${BASE_URL}/api/settings`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      approver_allowlist: ["priya", "alec", "security-lead"],
      passphrase_configured: false,
      github: {
        is_configured: false,
        status_message: "GitHub status not configured (local mode active)",
      },
      switch: {
        server_url: "http://localhost:8080",
        room_id: "warrant-room",
      },
      data_sources: {
        live_records: 0,
        seeded_records: 0,
      },
    };
  }
}

export async function seedDatabase(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/api/seed`, {
      method: "POST",
    });
    return res.ok;
  } catch (err) {
    return false;
  }
}
