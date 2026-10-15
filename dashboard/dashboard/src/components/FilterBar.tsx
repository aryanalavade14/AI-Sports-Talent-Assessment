import { useApi } from '../api';
import type { FilterOptions, Filters } from '../types';
import { NO_FILTERS } from '../types';
import { genderLabel } from './ui';

interface Props { filters: Filters; onChange: (f: Filters) => void }

export function FilterBar({ filters, onChange }: Props) {
  const { data: options } = useApi<FilterOptions>('/api/admin/filters');
  const set = (patch: Partial<Filters>) => onChange({ ...filters, ...patch });
  const active = Object.values(filters).some(Boolean);

  return (
    <div className="card" style={{ padding: 16, marginBottom: 16 }}>
      <div className="filters" style={{ marginBottom: 0 }}>
        <label className="field">
          <span>Region</span>
          <select value={filters.region} onChange={(e) => set({ region: e.target.value })}>
            <option value="">All regions</option>
            {options?.regions.map((r) => <option key={r}>{r}</option>)}
          </select>
        </label>
        <label className="field">
          <span>Sport</span>
          <select value={filters.sport} onChange={(e) => set({ sport: e.target.value })}>
            <option value="">All sports</option>
            {options?.sports.map((s) => <option key={s}>{s}</option>)}
          </select>
        </label>
        <label className="field">
          <span>Gender</span>
          <select value={filters.gender} onChange={(e) => set({ gender: e.target.value })}>
            <option value="">All</option>
            {(options?.genders ?? ['male', 'female']).map((g) => <option key={g} value={g}>{genderLabel(g)}</option>)}
          </select>
        </label>
        <div className="age-pair">
          <label className="field">
            <span>Min age{options?.age_min != null ? ` (${options.age_min}+)` : ''}</span>
            <input type="number" min={0} max={120} inputMode="numeric" value={filters.ageMin}
              onChange={(e) => set({ ageMin: e.target.value })} placeholder="Any" />
          </label>
          <label className="field">
            <span>Max age{options?.age_max != null ? ` (up to ${options.age_max})` : ''}</span>
            <input type="number" min={0} max={120} inputMode="numeric" value={filters.ageMax}
              onChange={(e) => set({ ageMax: e.target.value })} placeholder="Any" />
          </label>
        </div>
        <button className="btn secondary" disabled={!active} onClick={() => onChange(NO_FILTERS)}>Clear filters</button>
      </div>
    </div>
  );
}
