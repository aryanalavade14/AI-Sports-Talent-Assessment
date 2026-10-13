import { useCallback, useState } from 'react';
import { api, tokenStore, useAuthExpiry } from './api';
import { FilterBar } from './components/FilterBar';
import { Athletes } from './pages/Athletes';
import { Benchmarks } from './pages/Benchmarks';
import { Leaderboard } from './pages/Leaderboard';
import { Login } from './pages/Login';
import { Overview } from './pages/Overview';
import { Shortlist } from './pages/Shortlist';
import type { AthleteRow, Filters } from './types';
import { NO_FILTERS } from './types';

type Tab = 'overview' | 'athletes' | 'leaderboard' | 'benchmarks' | 'shortlist';
const TABS: { key: Tab; label: string; title: string; filters: boolean }[] = [
  { key: 'overview', label: 'Overview', title: 'Dashboard overview', filters: true },
  { key: 'athletes', label: 'Athletes', title: 'Athletes', filters: true },
  { key: 'leaderboard', label: 'Leaderboard', title: 'Leaderboard', filters: true },
  { key: 'benchmarks', label: 'Benchmarks', title: 'Benchmarks & percentiles', filters: false },
  { key: 'shortlist', label: 'Shortlist', title: 'Shortlist', filters: false },
];

export default function App() {
  const [authed, setAuthed] = useState(() => tokenStore.get() !== null);
  const [tab, setTab] = useState<Tab>('overview');
  const [filters, setFilters] = useState<Filters>(NO_FILTERS);
  const [version, setVersion] = useState(0); // bump to refetch after the shortlist changes
  const [toast, setToast] = useState<string | null>(null);

  useAuthExpiry(useCallback(() => setAuthed(false), []));

  const toggleShortlist = useCallback(async (row: AthleteRow) => {
    try {
      await api(`/api/admin/shortlist/${row.athlete_id}`, { method: row.shortlisted ? 'DELETE' : 'PUT' });
      setVersion((v) => v + 1);
      setToast(null);
    } catch (e) {
      setToast((e as Error).message);
    }
  }, []);

  if (!authed) return <Login onLoggedIn={() => setAuthed(true)} />;

  const current = TABS.find((t) => t.key === tab)!;
  const bump = () => setVersion((v) => v + 1);

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">🏅</div>
          <div><b>SPORTS TALENT AI</b><span className="caption">Admin / SAI dashboard</span></div>
        </div>
        <button className="btn secondary small" onClick={() => { tokenStore.clear(); setAuthed(false); }}>Sign out</button>
      </header>

      <nav className="nav" aria-label="Sections">
        {TABS.map((t) => (
          <button key={t.key} aria-current={tab === t.key ? 'page' : undefined} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </nav>

      <div className="page-title"><h1>{current.title}</h1></div>
      {toast && <div className="notice error" role="alert" style={{ marginBottom: 12 }}>{toast}</div>}
      {current.filters && <FilterBar filters={filters} onChange={setFilters} />}

      <main>
        {tab === 'overview' && <Overview filters={filters} version={version} onOpenAthletes={() => setTab('athletes')} />}
        {tab === 'athletes' && <Athletes filters={filters} version={version} onToggle={toggleShortlist} />}
        {tab === 'leaderboard' && <Leaderboard filters={filters} version={version} onToggle={toggleShortlist} />}
        {tab === 'benchmarks' && <Benchmarks />}
        {tab === 'shortlist' && <Shortlist version={version} onChanged={bump} />}
      </main>
    </div>
  );
}
