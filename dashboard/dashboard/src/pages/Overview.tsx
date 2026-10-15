import { filterQuery, useApi } from '../api';
import { HBars, LevelChart, SplitBar, sportBars } from '../components/BarCharts';
import { Empty, Status, LevelBadge, fmt } from '../components/ui';
import type { Filters, LeaderboardRow, Summary } from '../types';

function Metric({ label, value, unit, color }: { label: string; value: string; unit?: string; color: string }) {
  return (
    <div className="metric">
      <div className="dot" style={{ background: color }} />
      <div className="caption">{label}</div>
      <div className="value">{value}{unit && <span className="unit">{unit}</span>}</div>
    </div>
  );
}

export function Overview({ filters, version, onOpenAthletes }: { filters: Filters; version: number; onOpenAthletes: () => void }) {
  const summary = useApi<Summary>(`/api/admin/summary${filterQuery(filters)}`, version);
  const top = useApi<LeaderboardRow[]>(`/api/admin/leaderboard${filterQuery(filters, { limit: '5' })}`, version);
  const s = summary.data;

  return (
    <Status loading={summary.loading && !s} error={summary.error}>
      {s && s.total_athletes === 0 ? (
        <div className="card">
          <Empty title="No athletes found">
            {Object.values(filters).some(Boolean)
              ? 'No athletes match these filters. Try clearing some of them.'
              : 'Athletes appear here after they register in the mobile app and create their profile.'}
          </Empty>
        </div>
      ) : s ? (
        <>
          <div className="grid cards-6">
            <Metric label="Athletes" value={String(s.total_athletes)} color="var(--primary)" />
            <Metric label="Athletes tested" value={String(s.athletes_tested)} color="var(--cyan)" />
            <Metric label="Tests recorded" value={String(s.total_results)} color="var(--violet)" />
            <Metric label="Average percentile" value={fmt(s.average_percentile)} color="var(--success)" />
            <Metric label="Shortlisted" value={String(s.shortlisted)} color="var(--warning)" />
            <Metric label="Flagged results" value={String(s.flagged_results)} color="var(--danger)" />
          </div>
          <div className="grid cards-6" style={{ marginTop: 14, gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
            <Metric label="Average vertical jump" value={fmt(s.average_vertical_jump_cm)} unit="cm" color="var(--primary-bright)" />
            <Metric label="Average sit-ups (60 s)" value={fmt(s.average_sit_ups)} unit="reps" color="var(--primary-bright)" />
          </div>

          <div className="grid cards-2">
            <div className="card">
              <h3>Performance levels</h3>
              <p className="caption">Athletes by overall level vs. their age &amp; gender norm</p>
              {s.athletes_tested ? <LevelChart items={s.levels} /> : <Empty title="No test results yet" />}
            </div>
            <div className="card">
              <h3>Athletes by region</h3>
              <p className="caption">Top regions in the current selection</p>
              <HBars items={s.by_region.map((r) => ({ label: r.label, value: r.count }))} />
            </div>
            <div className="card">
              <h3>Average percentile by sport</h3>
              <p className="caption">Only athletes with at least one test · 50 = typical for their age &amp; gender</p>
              {s.by_sport.length ? <HBars items={sportBars(s.by_sport)} max={100} /> : <Empty title="No test results yet" />}
            </div>
            <div className="card">
              <h3>Gender split</h3>
              <p className="caption">All athletes in the current selection</p>
              <SplitBar items={s.by_gender} />
            </div>
          </div>

          <div className="card" style={{ marginTop: 14 }}>
            <div className="toolbar">
              <div><h3>Top athletes</h3><p className="caption">Highest overall percentile in the current selection</p></div>
              <button className="btn secondary small" onClick={onOpenAthletes}>View all athletes</button>
            </div>
            <Status loading={top.loading && !top.data} error={top.error}>
              {top.data && top.data.length > 0 ? (
                <div className="table-wrap">
                  <table style={{ minWidth: 520 }}>
                    <tbody>
                      {top.data.map((r) => (
                        <tr key={r.athlete_id}>
                          <td className="num" style={{ width: 40 }}><b>#{r.rank}</b></td>
                          <td><b>{r.name}</b> <span className="caption">{r.sport ?? ''} · {r.region ?? ''}</span></td>
                          <td className="num">{fmt(r.overall_percentile)}</td>
                          <td><LevelBadge level={r.overall_level} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : <Empty title="No ranked athletes yet" />}
            </Status>
          </div>
        </>
      ) : null}
    </Status>
  );
}
