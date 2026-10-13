import type { ReactNode } from 'react';
import type { AthleteRow } from '../types';

export const LEVEL_COLOR: Record<string, string> = {
  Excellent: 'var(--success)',
  Good: 'var(--cyan)',
  Average: 'var(--primary)',
  Developing: 'var(--warning)',
  'Needs Improvement': 'var(--danger)',
};

export function LevelBadge({ level }: { level: string | null }) {
  if (!level) return <span className="badge lvl-none">No data</span>;
  return <span className={`badge lvl-${level.replace(/ /g, '-')}`}>{level}</span>;
}

export function Meter({ value, color }: { value: number | null; color?: string }) {
  if (value === null) return <span className="caption">—</span>;
  return (
    <div className="meter" title={`${value}th percentile`}>
      <div className="track"><div className="fill" style={{ width: `${value}%`, background: color }} /></div>
      <b>{Math.round(value)}</b>
    </div>
  );
}

export function StarButton({ row, onToggle }: { row: AthleteRow; onToggle: (row: AthleteRow) => void }) {
  return (
    <button
      className={`star ${row.shortlisted ? 'on' : ''}`}
      onClick={() => onToggle(row)}
      aria-pressed={row.shortlisted}
      aria-label={row.shortlisted ? `Remove ${row.name} from shortlist` : `Shortlist ${row.name}`}
      title={row.shortlisted ? 'Remove from shortlist' : 'Shortlist this athlete'}
    >
      {row.shortlisted ? '★' : '☆'}
    </button>
  );
}

export function Status({ loading, error, children }: { loading: boolean; error: string | null; children?: ReactNode }) {
  if (error) return <div className="notice error" role="alert">{error}</div>;
  if (loading) return <div className="loading">Loading…</div>;
  return <>{children}</>;
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="empty">
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}

export const genderLabel = (g: string) => g.charAt(0).toUpperCase() + g.slice(1);
export const fmt = (n: number | null | undefined, digits = 1) =>
  n === null || n === undefined ? '—' : Number.isInteger(n) ? String(n) : n.toFixed(digits);
