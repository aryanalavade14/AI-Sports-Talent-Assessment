import { useCallback, useEffect, useState } from 'react';
import type { Filters } from './types';

// Empty string = same origin (the Vite dev server forwards /api to the backend).
const BASE: string = import.meta.env.VITE_API_URL && import.meta.env.PROD ? import.meta.env.VITE_API_URL : '';
const TOKEN_KEY = 'sta_admin_token';

export const tokenStore = {
  get(): string | null {
    try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
  },
  set(token: string) {
    try { localStorage.setItem(TOKEN_KEY, token); } catch { /* storage unavailable: stay logged in for this tab only */ }
    memoryToken = token;
  },
  clear() {
    try { localStorage.removeItem(TOKEN_KEY); } catch { /* ignore */ }
    memoryToken = null;
  },
};
let memoryToken: string | null = null;
const currentToken = () => memoryToken ?? tokenStore.get();

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = currentToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (init.body) headers.set('Content-Type', 'application/json');

  let res: Response;
  try {
    res = await fetch(BASE + path, { ...init, headers });
  } catch {
    throw new ApiError(0, 'Cannot reach the server. Is the backend running?');
  }
  if (res.status === 401 && path !== '/api/auth/login') {
    tokenStore.clear();
    window.dispatchEvent(new Event('auth-expired'));
  }
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === 'string') detail = body.detail;
      else if (Array.isArray(body.detail)) detail = body.detail.map((d: { msg: string }) => d.msg).join(', ');
    } catch { /* not JSON */ }
    throw new ApiError(res.status, detail);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

/** Build "?region=...&gender=..." from the filter bar, skipping empty values. */
export function filterQuery(f: Filters, extra: Record<string, string> = {}): string {
  const p = new URLSearchParams();
  if (f.region) p.set('region', f.region);
  if (f.sport) p.set('sport', f.sport);
  if (f.gender) p.set('gender', f.gender);
  if (f.ageMin) p.set('age_min', f.ageMin);
  if (f.ageMax) p.set('age_max', f.ageMax);
  Object.entries(extra).forEach(([k, v]) => p.set(k, v));
  const q = p.toString();
  return q ? `?${q}` : '';
}

/** Tiny data-loading hook: refetches when `path` (or `version`) changes. */
export function useApi<T>(path: string | null, version = 0) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(path !== null);

  useEffect(() => {
    if (path === null) return;
    let cancelled = false;
    setLoading(true);
    api<T>(path)
      .then((d) => { if (!cancelled) { setData(d); setError(null); } })
      .catch((e: Error) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [path, version]);

  return { data, error, loading };
}

export function useAuthExpiry(onExpire: () => void) {
  const cb = useCallback(onExpire, [onExpire]);
  useEffect(() => {
    window.addEventListener('auth-expired', cb);
    return () => window.removeEventListener('auth-expired', cb);
  }, [cb]);
}
