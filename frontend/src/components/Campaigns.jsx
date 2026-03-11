import { useState, useEffect } from 'react'
import api from '../api'

export default function Campaigns({ onSelect }) {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/campaigns/').then(res => {
      setCampaigns(res.data)
      setLoading(false)
    })
  }, [])

  return (
    <div>
      <div className="page-title">Campaigns</div>
      <div className="page-subtitle">Manage and monitor your phishing simulation campaigns</div>
      <div className="card">
        {loading ? (
          <p style={{color: '#64748b'}}>Loading campaigns...</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map(c => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.campaign_type}</td>
                  <td><span className={`badge ${c.status}`}>{c.status}</span></td>
                  <td>{new Date(c.created_at).toLocaleDateString()}</td>
                  <td>
                    <button className="btn btn-secondary" onClick={() => onSelect(c)}>
                      View
                    </button>
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