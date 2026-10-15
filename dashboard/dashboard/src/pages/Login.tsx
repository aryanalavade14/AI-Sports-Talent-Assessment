import { FormEvent, useState } from 'react';
import { ApiError, api, tokenStore } from '../api';

interface LoginResponse { access_token: string; user: { role: string } }

export function Login({ onLoggedIn }: { onLoggedIn: () => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await api<LoginResponse>('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
      if (res.user.role !== 'admin') { setError('This dashboard is for admin / SAI accounts only.'); return; }
      tokenStore.set(res.access_token);
      onLoggedIn();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Login failed');
    } finally { setBusy(false); }
  };

  return (
    <div className="login">
      <form className="card" onSubmit={submit}>
        <div className="brand"><div className="brand-mark">🏅</div><div><b>SPORTS TALENT AI</b><span className="caption">Admin / SAI dashboard</span></div></div>
        <label className="field"><span>Email</span><input type="email" required autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label className="field"><span>Password</span><input type="password" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        {error && <div className="notice error" role="alert">{error}</div>}
        <button className="btn" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
        <p className="caption">Admin accounts are created with <code>python -m app.utils.create_admin</code> in the backend.</p>
      </form>
    </div>
  );
}
