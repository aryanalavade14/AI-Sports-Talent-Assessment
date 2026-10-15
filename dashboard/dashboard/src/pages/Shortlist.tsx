import { useState } from 'react';
import { api, useApi } from '../api';
import { ScoreLine, WhoLine } from '../components/AthleteList';
import { Empty, LevelBadge, Meter, Status, fmt } from '../components/ui';
import type { ShortlistEntry } from '../types';

function csvCell(v: string | number | null | undefined) {
  const s = v === null || v === undefined ? '' : String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function downloadCsv(entries: ShortlistEntry[]) {
  const head = ['Name', 'Age', 'Gender', 'Sport', 'Region', 'Vertical jump (cm)', 'Sit-ups (reps)', 'Overall percentile', 'Level', 'Note'];
  const lines = entries.map(({ athlete: a, note }) => [
    a.name, a.age, a.gender, a.sport, a.region, a.vertical_jump?.value, a.sit_up?.value, a.overall_percentile, a.overall_level, note,
  ].map(csvCell).join(','));
  const url = URL.createObjectURL(new Blob([[head.join(','), ...lines].join('\n')], { type: 'text/csv' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'shortlisted-athletes.csv';
  link.click();
  URL.revokeObjectURL(url);
}

function Entry({ entry, onChanged, onError }: { entry: ShortlistEntry; onChanged: () => void; onError: (m: string) => void }) {
  const a = entry.athlete;
  const [note, setNote] = useState(entry.note ?? '');
  const [saving, setSaving] = useState(false);
  const dirty = note.trim() !== (entry.note ?? '');

  const save = async () => {
    setSaving(true);
    try {
      await api(`/api/admin/shortlist/${a.athlete_id}`, { method: 'PUT', body: JSON.stringify({ note }) });
      onChanged();
    } catch (e) { onError((e as Error).message); } finally { setSaving(false); }
  };
  const remove = async () => {
    try { await api(`/api/admin/shortlist/${a.athlete_id}`, { method: 'DELETE' }); onChanged(); }
    catch (e) { onError((e as Error).message); }
  };

  return (
    <div className="card" style={{ padding: 16 }}>
      <div className="rank-row flat">
        <WhoLine row={a} />
        <ScoreLine row={a} />
        <div className="right"><div style={{ minWidth: 100 }}><Meter value={a.overall_percentile} color="var(--cyan)" /></div><LevelBadge level={a.overall_level} /></div>
      </div>
      <div style={{ display: 'flex', gap: 10, marginTop: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <label className="field" style={{ flex: '1 1 240px' }}>
          <span>Scout note</span>
          <input value={note} maxLength={500} placeholder="Why is this athlete promising?" onChange={(e) => setNote(e.target.value)} />
        </label>
        <button className="btn small" disabled={!dirty || saving} onClick={save}>{saving ? 'Saving…' : 'Save note'}</button>
        <button className="btn secondary small danger-text" onClick={remove}>Remove</button>
      </div>
      <p className="caption" style={{ marginTop: 8 }}>Shortlisted {new Date(entry.shortlisted_at).toLocaleDateString()} · overall percentile {fmt(a.overall_percentile)}</p>
    </div>
  );
}

export function Shortlist({ version, onChanged }: { version: number; onChanged: () => void }) {
  const { data, error, loading } = useApi<ShortlistEntry[]>('/api/admin/shortlist', version);
  const [problem, setProblem] = useState<string | null>(null);

  return (
    <Status loading={loading && !data} error={error}>
      <div className="toolbar">
        <div><h2>Shortlisted athletes</h2><p className="caption">Promising athletes you have marked with ★ · not affected by the filters</p></div>
        <button className="btn secondary small" disabled={!data?.length} onClick={() => data && downloadCsv(data)}>Download CSV</button>
      </div>
      {problem && <div className="notice error" role="alert" style={{ marginBottom: 12 }}>{problem}</div>}
      {data && data.length > 0 ? (
        <div className="list">
          {data.map((e) => <Entry key={e.athlete.athlete_id} entry={e} onChanged={onChanged} onError={setProblem} />)}
        </div>
      ) : (
        <div className="card"><Empty title="No one shortlisted yet">Tap the ☆ next to an athlete in the Athletes or Leaderboard pages to add them here.</Empty></div>
      )}
    </Status>
  );
}
