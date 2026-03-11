import { useState, useEffect } from 'react'
import api from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function CampaignDetail({ campaign, onBack }) {
  const [targets, setTargets] = useState([])
  const [newTarget, setNewTarget] = useState({
    first_name: '', last_name: '', email: '', department: ''
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/targets/${campaign.id}/targets`).then(res => {
      setTargets(res.data)
      setLoading(false)
    })
  }, [campaign.id])

  const addTarget = async () => {
    try {
      const res = await api.post(`/targets/${campaign.id}/targets`, newTarget)
      setTargets([...targets, res.data])
      setNewTarget({ first_name: '', last_name: '', email: '', department: '' })
    } catch (e) {
      alert('Failed to add target')
    }
  }

  const chartData = [
    { name: 'Targets', value: targets.length, fill: '#3b82f6' },
  ]

  return (
    <div>
      <button className="btn btn-secondary" onClick={onBack} style={{marginBottom: '16px'}}>
        Back to Campaigns
      </button>
      <div className="page-title">{campaign.name}</div>
      <div className="page-subtitle">{campaign.campaign_type} — {campaign.status}</div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="label">Total Targets</div>
          <div className="value blue">{targets.length}</div>
        </div>
        <div className="stat-card">
          <div className="label">Campaign Type</div>
          <div className="value" style={{fontSize: '16px', marginTop: '8px'}}>{campaign.campaign_type}</div>
        </div>
        <div className="stat-card">
          <div className="label">Status</div>
          <div className="value" style={{fontSize: '16px', marginTop: '8px'}}>
            <span className={`badge ${campaign.status}`}>{campaign.status}</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Created</div>
          <div className="value" style={{fontSize: '16px', marginTop: '8px'}}>
            {new Date(campaign.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>

      <div className="card">
        <h3 style={{marginBottom: '20px'}}>Add Target</h3>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px'}}>
          <div>
            <label className="form-label">First Name</label>
            <input value={newTarget.first_name}
              onChange={e => setNewTarget({...newTarget, first_name: e.target.value})}
              placeholder="John" />
          </div>
          <div>
            <label className="form-label">Last Name</label>
            <input value={newTarget.last_name}
              onChange={e => setNewTarget({...newTarget, last_name: e.target.value})}
              placeholder="Smith" />
          </div>
          <div>
            <label className="form-label">Email</label>
            <input value={newTarget.email}
              onChange={e => setNewTarget({...newTarget, email: e.target.value})}
              placeholder="john@company.com" />
          </div>
          <div>
            <label className="form-label">Department</label>
            <input value={newTarget.department}
              onChange={e => setNewTarget({...newTarget, department: e.target.value})}
              placeholder="Finance" />
          </div>
        </div>
        <button className="btn btn-primary" onClick={addTarget}>Add Target</button>
      </div>

      <div className="card">
        <h3 style={{marginBottom: '20px'}}>Targets ({targets.length})</h3>
        {loading ? (
          <p style={{color: '#64748b'}}>Loading...</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Training</th>
                <th>Tracking UUID</th>
              </tr>
            </thead>
            <tbody>
              {targets.map(t => (
                <tr key={t.id}>
                  <td>{t.first_name} {t.last_name}</td>
                  <td>{t.email}</td>
                  <td>{t.department}</td>
                  <td>
                    <span className={`badge ${t.training_completed ? 'active' : 'draft'}`}>
                      {t.training_completed ? 'Complete' : 'Pending'}
                    </span>
                  </td>
                  <td style={{color: '#64748b', fontSize: '12px', fontFamily: 'monospace'}}>
                    {t.tracking_uuid.substring(0, 8)}...
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}