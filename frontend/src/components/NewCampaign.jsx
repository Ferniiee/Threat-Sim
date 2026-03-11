import { useState } from 'react'
import api from '../api'

export default function NewCampaign({ onCreated }) {
  const [form, setForm] = useState({
    name: '',
    subject: '',
    body: '',
    campaign_type: 'credential-harvest'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCreate = async () => {
    setLoading(true)
    setError('')
    try {
      await api.post('/campaigns/', form)
      onCreated()
    } catch (e) {
      setError('Failed to create campaign')
    }
    setLoading(false)
  }

  return (
    <div>
      <div className="page-title">New Campaign</div>
      <div className="page-subtitle">Create a new phishing simulation campaign</div>
      <div className="card" style={{maxWidth: '600px'}}>
        {error && <div className="error">{error}</div>}
        <label className="form-label">Campaign Name</label>
        <input
          value={form.name}
          onChange={e => setForm({...form, name: e.target.value})}
          placeholder="Q1 Password Reset Test"
        />
        <label className="form-label">Email Subject</label>
        <input
          value={form.subject}
          onChange={e => setForm({...form, subject: e.target.value})}
          placeholder="ACTION REQUIRED: Reset your password"
        />
        <label className="form-label">Campaign Type</label>
        <select
          value={form.campaign_type}
          onChange={e => setForm({...form, campaign_type: e.target.value})}
        >
          <option value="credential-harvest">Credential Harvest</option>
          <option value="urgency">Urgency Manipulation</option>
          <option value="attachment-lure">Attachment Lure</option>
        </select>
        <label className="form-label">Email Body</label>
        <textarea
          rows={6}
          value={form.body}
          onChange={e => setForm({...form, body: e.target.value})}
          placeholder="Hi {{first_name}}, your {{department}} account requires attention..."
        />
        <button className="btn btn-primary" onClick={handleCreate} disabled={loading}>
          {loading ? 'Creating...' : 'Create Campaign'}
        </button>
      </div>
    </div>
  )
}