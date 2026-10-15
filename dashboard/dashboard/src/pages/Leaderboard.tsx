import { useState } from 'react';
import { filterQuery, useApi } from '../api';
import { ScoreLine, WhoLine } from '../components/AthleteList';
import { Empty, LevelBadge, Meter, Status, StarButton } from '../components/ui';
import type { AthleteRow, Filters, LeaderboardRow } from '../types';

type Board = 'overall' | 'vertical_jump' | 'sit_up';
const BOARDS: { key: Board; label: string }[] = [
  { key: 'overall', label: 'Overall' },
  { key: 'vertical_jump', label: 'Vertical Jump' },
  { key: 'sit_up', label: 'Sit-ups' },
];

export function Leaderboard({ filters, version, onToggle }: { filters: Filters; version: number; onToggle: (r: AthleteRow) => void }) {
  const [board, setBoard] = useState<Board>('overall');
  const { data, error, loading } = useApi<LeaderboardRow[]>(`/api/admin/leaderboard${filterQuery(filters, { test: board, limit: '50' })}`, version);

  const percentileOf = (r: LeaderboardRow) => (board === 'overall' ? r.overall_percentile : r[board]?.percentile ?? null);
  const levelOf = (r: LeaderboardRow) => (board === 'overall' ? r.overall_level : r[board]?.level ?? null);

  return (
    <div className="card">
      <div className="toolbar">
        <div>
          <h3>Leaderboard</h3>
          <p className="caption">Ranked by percentile, so athletes of different ages and genders compare fairly. Ties go to the higher raw score.</p>
        </div>
        <div className="seg" role="group" aria-label="Leaderboard type">
          {BOARDS.map((b) => (
            <button key={b.key} aria-pressed={board === b.key} onClick={() => setBoard(b.key)}>{b.label}</button>
          ))}
        </div>
      </div>
      <Status loading={loading && !data} error={error}>
        {data && data.length > 0 ? (
          <div className="list">
            {data.map((r) => (
              <div key={r.athlete_id} className={`rank-row ${r.rank <= 3 ? `r${r.rank}` : ''}`}>
                <div className="rank">{r.rank}</div>
                <WhoLine row={r} />
                <ScoreLine row={r} />
                <div className="right">
                  <div style={{ minWidth: 110 }}><Meter value={percentileOf(r)} color="var(--cyan)" /></div>
                  <LevelBadge level={levelOf(r)} />
                  <StarButton row={r} onToggle={onToggle} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <Empty title="Nobody to rank yet">
            Athletes appear here once they have a completed test that is not flagged, and match the current filters.
          </Empty>
        )}
      </Status>
    </div>
  );
}
