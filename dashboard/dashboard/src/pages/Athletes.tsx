import { useMemo, useState } from 'react';
import { filterQuery, useApi } from '../api';
import { Empty, LevelBadge, Meter, Status, StarButton, fmt, genderLabel } from '../components/ui';
import type { AthleteRow, Filters, TestKey } from '../types';
import { TEST_LABEL } from '../types';

type SortKey = 'name' | 'age' | 'vj' | 'vjp' | 'su' | 'sup' | 'overall';
const PAGE = 15;
const MAX_COMPARE = 4;

const sorters: Record<SortKey, (r: AthleteRow) => number | string> = {
  name: (r) => r.name.toLowerCase(),
  age: (r) => r.age,
  vj: (r) => r.vertical_jump?.value ?? -1,
  vjp: (r) => r.vertical_jump?.percentile ?? -1,
  su: (r) => r.sit_up?.value ?? -1,
  sup: (r) => r.sit_up?.percentile ?? -1,
  overall: (r) => r.overall_percentile ?? -1,
};

export function Athletes({ filters, version, onToggle }: { filters: Filters; version: number; onToggle: (r: AthleteRow) => void }) {
  const { data, error, loading } = useApi<AthleteRow[]>(`/api/admin/athletes${filterQuery(filters)}`, version);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 }>({ key: 'overall', dir: -1 });
  const [page, setPage] = useState(0);
  const [picked, setPicked] = useState<Record<string, AthleteRow>>({});
  const [comparing, setComparing] = useState(false);

  const rows = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = (data ?? []).filter((r) => !q || r.name.toLowerCase().includes(q));
    return [...list].sort((a, b) => {
      const x = sorters[sort.key](a), y = sorters[sort.key](b);
      return (x < y ? -1 : x > y ? 1 : 0) * sort.dir;
    });
  }, [data, search, sort]);

  const pages = Math.max(1, Math.ceil(rows.length / PAGE));
  const current = Math.min(page, pages - 1);
  const visible = rows.slice(current * PAGE, current * PAGE + PAGE);
  const pickedList = Object.values(picked).map((p) => data?.find((r) => r.athlete_id === p.athlete_id) ?? p);

  const toggleSort = (key: SortKey) => {
    setSort((s) => (s.key === key ? { key, dir: (s.dir * -1) as 1 | -1 } : { key, dir: key === 'name' ? 1 : -1 }));
    setPage(0);
  };
  const toggleCompare = (r: AthleteRow) =>
    setPicked((p) => {
      if (p[r.athlete_id]) { const { [r.athlete_id]: _gone, ...rest } = p; return rest; }
      return Object.keys(p).length >= MAX_COMPARE ? p : { ...p, [r.athlete_id]: r };
    });

  const Th = ({ k, children, num }: { k: SortKey; children: string; num?: boolean }) => (
    <th className={`sortable ${num ? 'num' : ''}`} onClick={() => toggleSort(k)} aria-sort={sort.key === k ? (sort.dir === 1 ? 'ascending' : 'descending') : 'none'}>
      {children}{sort.key === k ? (sort.dir === 1 ? ' ▲' : ' ▼') : ''}
    </th>
  );

  return (
    <Status loading={loading && !data} error={error}>
      <div className="card">
        <div className="toolbar">
          <div>
            <h3>Athlete comparison</h3>
            <p className="caption">
              {rows.length} athlete(s) · scores are each athlete's best clean result · tick up to {MAX_COMPARE} athletes to compare side by side
            </p>
          </div>
          <label className="field" style={{ minWidth: 220 }}>
            <span className="sr-only">Search by name</span>
            <input type="search" placeholder="Search by name…" value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} />
          </label>
        </div>

        {rows.length === 0 ? (
          <Empty title="No athletes found">
            {data?.length === 0 ? 'No athletes match these filters, or none have registered yet.' : 'No athlete matches that name.'}
          </Empty>
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th aria-label="Compare" />
                    <th aria-label="Shortlist" />
                    <Th k="name">Athlete</Th>
                    <Th k="age" num>Age</Th>
                    <th>Gender</th>
                    <th>Sport</th>
                    <th>Region</th>
                    <Th k="vj" num>Jump (cm)</Th>
                    <Th k="vjp">Jump %ile</Th>
                    <Th k="su" num>Sit-ups</Th>
                    <Th k="sup">Sit-up %ile</Th>
                    <Th k="overall">Overall %ile</Th>
                    <th>Level</th>
                  </tr>
                </thead>
                <tbody>
                  {visible.map((r) => (
                    <tr key={r.athlete_id}>
                      <td>
                        <input type="checkbox" style={{ width: 18, minHeight: 18 }} checked={!!picked[r.athlete_id]}
                          disabled={!picked[r.athlete_id] && pickedList.length >= MAX_COMPARE}
                          onChange={() => toggleCompare(r)} aria-label={`Compare ${r.name}`} />
                      </td>
                      <td><StarButton row={r} onToggle={onToggle} /></td>
                      <td className="name-cell">
                        <b>{r.name}</b>
                        {r.flagged_results > 0 && (
                          <span className="warn-flag" title={`${r.flagged_results} result(s) flagged by cheat detection and not counted`}>⚠ {r.flagged_results}</span>
                        )}
                      </td>
                      <td className="num">{r.age}</td>
                      <td>{genderLabel(r.gender)}</td>
                      <td>{r.sport ?? '—'}</td>
                      <td>{r.region ?? '—'}</td>
                      <td className="num">{fmt(r.vertical_jump?.value)}</td>
                      <td><Meter value={r.vertical_jump?.percentile ?? null} /></td>
                      <td className="num">{fmt(r.sit_up?.value)}</td>
                      <td><Meter value={r.sit_up?.percentile ?? null} /></td>
                      <td><Meter value={r.overall_percentile} color="var(--cyan)" /></td>
                      <td><LevelBadge level={r.overall_level} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pager">
              <span className="caption">Page {current + 1} of {pages}</span>
              <button className="btn secondary small" disabled={current === 0} onClick={() => setPage(current - 1)}>Previous</button>
              <button className="btn secondary small" disabled={current >= pages - 1} onClick={() => setPage(current + 1)}>Next</button>
            </div>
          </>
        )}
      </div>

      {pickedList.length > 0 && (
        <div className="compare-bar">
          <span><b>{pickedList.length}</b> selected: {pickedList.map((p) => p.name).join(', ')}</span>
          <span style={{ display: 'flex', gap: 8 }}>
            <button className="btn secondary small" onClick={() => { setPicked({}); setComparing(false); }}>Clear</button>
            <button className="btn small" disabled={pickedList.length < 2} onClick={() => setComparing(true)}>
              {pickedList.length < 2 ? 'Pick one more' : 'Compare'}
            </button>
          </span>
        </div>
      )}

      {comparing && pickedList.length >= 2 && (
        <div className="card" style={{ marginTop: 14 }}>
          <div className="toolbar">
            <div><h3>Side-by-side comparison</h3><p className="caption">The line in each bar marks the 50th percentile (typical for that athlete's age &amp; gender)</p></div>
            <button className="btn secondary small" onClick={() => setComparing(false)}>Close</button>
          </div>
          <div className="compare-grid">
            {pickedList.map((r) => (
              <div className="compare-card" key={r.athlete_id}>
                <div>
                  <b>{r.name}</b>
                  <div className="caption">{r.age} yrs · {genderLabel(r.gender)} · {r.sport ?? 'No sport'} · {r.region ?? 'No region'}</div>
                </div>
                {(['vertical_jump', 'sit_up'] as TestKey[]).map((t) => {
                  const s = r[t];
                  return (
                    <div key={t}>
                      <div className="caption">{TEST_LABEL[t]}</div>
                      {s ? (
                        <>
                          <div><b style={{ fontSize: 20 }}>{fmt(s.value)}</b> <span className="caption">{s.unit} · typical {fmt(s.norm_median)}</span></div>
                          <div className="pct-bar" title={s.norm_reference ?? ''}>
                            <div className="fill" style={{ width: `${s.percentile ?? 0}%` }} /><div className="mid" />
                          </div>
                          <div className="caption" style={{ marginTop: 4 }}>{fmt(s.percentile)} percentile · {s.level}</div>
                        </>
                      ) : <div className="caption">Not tested</div>}
                    </div>
                  );
                })}
                <div>
                  <div className="caption">Overall</div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}><b style={{ fontSize: 20 }}>{fmt(r.overall_percentile)}</b><LevelBadge level={r.overall_level} /></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Status>
  );
}
