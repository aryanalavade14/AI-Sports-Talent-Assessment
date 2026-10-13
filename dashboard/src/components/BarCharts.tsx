import type { AvgItem, CountItem } from '../types';
import { LEVEL_COLOR } from './ui';

/** Vertical bars: how many athletes are in each performance level. */
export function LevelChart({ items }: { items: CountItem[] }) {
  const max = Math.max(1, ...items.map((i) => i.count));
  return (
    <div className="cols" role="img" aria-label={items.map((i) => `${i.label}: ${i.count}`).join(', ')}>
      {items.map((i) => (
        <div className="col" key={i.label}>
          <span className="n">{i.count}</span>
          <div className="bar" style={{ height: `${(i.count / max) * 100}%`, background: LEVEL_COLOR[i.label] }} />
          <span className="l">{i.label}</span>
        </div>
      ))}
    </div>
  );
}

/** Horizontal bars with a number on the right. */
export function HBars({ items, max, suffix = '' }: { items: { label: string; value: number; note?: string }[]; max?: number; suffix?: string }) {
  const top = max ?? Math.max(1, ...items.map((i) => i.value));
  return (
    <div className="bars">
      {items.map((i) => (
        <div className="hbar" key={i.label} title={i.note}>
          <span className="label">{i.label}</span>
          <div className="track"><div className="fill" style={{ width: `${(i.value / top) * 100}%` }} /></div>
          <span className="val">{i.value}{suffix}</span>
        </div>
      ))}
    </div>
  );
}

export const sportBars = (items: AvgItem[]) =>
  items.map((s) => ({ label: s.label, value: s.average_percentile, note: `${s.athletes} athlete(s)` }));

/** One stacked bar (gender split) with a legend. */
export function SplitBar({ items }: { items: CountItem[] }) {
  const total = items.reduce((a, i) => a + i.count, 0) || 1;
  const colors = ['var(--primary)', 'var(--violet)', 'var(--cyan)'];
  return (
    <>
      <div className="stack" role="img" aria-label={items.map((i) => `${i.label}: ${i.count}`).join(', ')}>
        {items.map((i, idx) => <div key={i.label} style={{ width: `${(i.count / total) * 100}%`, background: colors[idx % 3] }} />)}
      </div>
      <div className="legend">
        {items.map((i, idx) => (
          <span key={i.label}><i style={{ background: colors[idx % 3] }} />{i.label} · {i.count} ({Math.round((i.count / total) * 100)}%)</span>
        ))}
      </div>
    </>
  );
}
