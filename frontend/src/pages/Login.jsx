import { useState } from 'react'
import api from '../api'

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/auth/login', { email, password })
      onLogin(res.data.access_token)
    } catch (e) {
      setError('Invalid email or password')
    }
    setLoading(false)
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>ThreatSim</h1>
        <p>Phishing simulation & security awareness platform</p>
        {error && <div className="error">{error}</div>}
        <label className="form-label">Email</label>
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="admin@threatsim.com"
        />
        <label className="form-label">Password</label>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="••••••••"
          onKeyDown={e => e.key === 'Enter' && handleLogin()}
        />
        <button
          className="btn btn-primary"
          style={{width: '100%', marginTop: '8px'}}
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </div>
    </div>
  )
}