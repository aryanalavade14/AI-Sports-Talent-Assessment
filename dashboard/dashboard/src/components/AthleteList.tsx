import { genderLabel, fmt } from './ui';
import type { AthleteRow } from '../types';

/** Compact score line used by the leaderboard and shortlist pages. */
export function ScoreLine({ row }: { row: AthleteRow }) {
  return (
    <div className="scores">
      <div><span className="caption">Vertical jump</span><b>{row.vertical_jump ? `${fmt(row.vertical_jump.value)} cm` : '—'}</b></div>
      <div><span className="caption">Sit-ups</span><b>{row.sit_up ? `${fmt(row.sit_up.value)} reps` : '—'}</b></div>
    </div>
  );
}

export function WhoLine({ row }: { row: AthleteRow }) {
  return (
    <div>
      <b>{row.name}</b>
      <div className="caption">
        {row.age} yrs · {genderLabel(row.gender)} · {row.sport ?? 'No sport'} · {row.region ?? 'No region'}
      </div>
    </div>
  );
}
