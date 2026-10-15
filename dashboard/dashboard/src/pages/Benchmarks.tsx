import { FormEvent, useState } from 'react';
import { ApiError, api, useApi } from '../api';
import { LevelBadge, Status, genderLabel } from '../components/ui';
import type { Evaluation, Norm, TestKey } from '../types';
import { TEST_LABEL, TEST_UNIT } from '../types';

function Calculator() {
  const [test, setTest] = useState<TestKey>('vertical_jump');
  const [gender, setGender] = useState('male');
  const [age, setAge] = useState('16');
  const [value, setValue] = useState('');
  const [result, setResult] = useState<Evaluation | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const q = new URLSearchParams({ test_type: test, gender, age, value });
      setResult(await api<Evaluation>(`/api/benchmarks/evaluate?${q}`));
    } catch (err) {
      setResult(null);
      setError(err instanceof ApiError ? err.message : 'Something went wrong');
    }
  };

  return (
    <div className="card">
      <h3>Check a score</h3>
      <p className="caption">Type a result to see where it ranks against the norm for that age and gender</p>
      <form onSubmit={submit} className="filters" style={{ marginTop: 14, marginBottom: 0 }}>
        <label className="field"><span>Test</span>
          <select value={test} onChange={(e) => setTest(e.target.value as TestKey)}>
            {(Object.keys(TEST_LABEL) as TestKey[]).map((t) => <option key={t} value={t}>{TEST_LABEL[t]}</option>)}
          </select></label>
        <label className="field"><span>Gender</span>
          <select value={gender} onChange={(e) => setGender(e.target.value)}>
            <option value="male">Male</option><option value="female">Female</option><option value="other">Other</option>
          </select></label>
        <label className="field"><span>Age</span>
          <input type="number" min={5} max={100} required value={age} onChange={(e) => setAge(e.target.value)} /></label>
        <label className="field"><span>Score ({TEST_UNIT[test]})</span>
          <input type="number" min={0} step="any" required value={value} onChange={(e) => setValue(e.target.value)} /></label>
        <button className="btn" type="submit">Calculate</button>
      </form>
      {error && <div className="notice error" role="alert" style={{ marginTop: 14 }}>{error}</div>}
      {result && (
        <div className="result-box">
          <div style={{ display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
            <span className="big-pct">{result.percentile}</span>
            <div><div className="caption">percentile</div><LevelBadge level={result.level} /></div>
          </div>
          <div className="pct-bar"><div className="fill" style={{ width: `${result.percentile}%` }} /><div className="mid" /></div>
          <p className="caption">
            {result.value} {TEST_UNIT[result.test_type]} · typical score for this group: {result.median} · {result.norm_reference}
          </p>
        </div>
      )}
    </div>
  );
}

function NormTable({ test, norms }: { test: TestKey; norms: Norm[] }) {
  const rows = norms.filter((n) => n.test_type === test);
  const genders = [...new Set(rows.map((n) => n.gender))];
  return (
    <div className="card">
      <h3>{TEST_LABEL[test]} norms</h3>
      <p className="caption">Score ({TEST_UNIT[test]}) needed to reach each percentile</p>
      {genders.map((g) => (
        <div key={g} style={{ marginTop: 14 }}>
          <b>{genderLabel(g)}</b>
          <div className="table-wrap">
            <table className="norm-table">
              <thead><tr><th>Age</th><th className="num">10th</th><th className="num">25th</th><th className="num">50th</th><th className="num">75th</th><th className="num">90th</th></tr></thead>
              <tbody>
                {rows.filter((n) => n.gender === g).map((n) => (
                  <tr key={`${g}-${n.age_min}`}>
                    <td>{n.age_max >= 100 ? `${n.age_min}+` : `${n.age_min}–${n.age_max}`}</td>
                    <td className="num">{n.p10}</td><td className="num">{n.p25}</td><td className="num"><b>{n.p50}</b></td><td className="num">{n.p75}</td><td className="num">{n.p90}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}

export function Benchmarks() {
  const { data, error, loading } = useApi<Norm[]>('/api/benchmarks/norms');
  const source = data?.[0]?.source;
  return (
    <div className="row-gap">
      <Calculator />
      <Status loading={loading} error={error}>
        {data && data.length === 0 && <div className="notice">No norms found. Run <code>python -m alembic upgrade head</code> in the backend folder.</div>}
        {data && data.length > 0 && (
          <>
            <div className="two-col">
              <NormTable test="vertical_jump" norms={data} />
              <NormTable test="sit_up" norms={data} />
            </div>
            <div className="notice">
              <b>How percentiles work:</b> a score is placed between the 10th–90th percentile points of its age and gender group
              (e.g. a 50th percentile score equals the group's typical result). Levels: 80+ Excellent · 60–79 Good · 40–59 Average ·
              20–39 Developing · below 20 Needs Improvement. Athletes with gender “other” use the average of the male and female norms.
              Source of the norm table: {source}. Norms are stored in the <code>benchmark_norms</code> database table.
            </div>
          </>
        )}
      </Status>
    </div>
  );
}
