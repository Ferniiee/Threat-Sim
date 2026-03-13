import { useState, useEffect } from 'react'
import api from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'

const COLORS = ['#ef4444', '#f59e0b', '#10b981', '#64748b']

export default function Analytics({ campaign }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get(`/analytics/campaigns/${campaign.id}`)
      .then(res => {
        setData(res.data)
        setLoading(false)
      })
      .catch(err => {
        setError('Failed to load analytics')
        setLoading(false)
      })
  }, [campaign.id])

  if (loading) return <p style={{color: '#64748b', padding: '20px'}}>Loading analytics...</p>
  if (error) return <p style={{color: '#ef4444', padding: '20px'}}>{error}</p>
  if (!data) return null

  const rateData = [
    { name: 'Open Rate', value: data.open_rate, fill: '#f59e0b' },
    { name: 'Click Rate', value: data.click_rate, fill: '#ef4444' },
    { name: 'Report Rate', value: data.report_rate, fill: '#10b981' },
  ]

  const noAction = Math.max(0, data.total_targets - data.clicked - data.reported)
  const pieData = [
    { name: 'Clicked', value: data.clicked || 0 },
    { name: 'Reported', value: data.reported || 0 },
    { name: 'No Action', value: noAction },
  ].filter(d => d.value > 0)

  return (
    <div>
      <div className="stat-grid">
        <div className="stat-card">
          <div className="label">Total Targets</div>
          <div className="value blue">{data.total_targets}</div>
        </div>
        <div className="stat-card">
          <div className="label">Click Rate</div>
          <div className="value red">{data.click_rate}%</div>
        </div>
        <div className="stat-card">
          <div className="label">Report Rate</div>
          <div className="value green">{data.report_rate}%</div>
        </div>
        <div className="stat-card">
          <div className="label">Training Done</div>
          <div className="value yellow">{data.training_completed}</div>
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px'}}>
        <div className="card">
          <h3 style={{marginBottom: '20px'}}>Engagement Rates</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={rateData}>
              <XAxis dataKey="name" tick={{fill: '#64748b', fontSize: 12}} />
              <YAxis tick={{fill: '#64748b', fontSize: 12}} unit="%" domain={[0, 100]} />
              <Tooltip
                contentStyle={{background: '#1a1d27', border: '1px solid #2d3748', borderRadius: '8px'}}
                formatter={(v) => `${v}%`}
              />
              <Bar dataKey="value" radius={[4,4,0,0]}>
                {rateData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 style={{marginBottom: '20px'}}>Target Response Breakdown</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({name, value}) => `${name}: ${value}`}
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={COLORS[i]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{background: '#1a1d27', border: '1px solid #2d3748', borderRadius: '8px'}}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{color: '#64748b'}}>No interaction data yet.</p>
          )}
        </div>
      </div>

      {data.targets && data.targets.length > 0 && (
        <div className="card">
          <h3 style={{marginBottom: '20px'}}>Per-Target Breakdown</h3>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Department</th>
                <th>Opened</th>
                <th>Clicked</th>
                <th>Reported</th>
                <th>Training</th>
              </tr>
            </thead>
            <tbody>
              {data.targets.map(t => (
                <tr key={t.target_id}>
                  <td>{t.name}</td>
                  <td>{t.department}</td>
                  <td>{t.opened ? <span className="badge open">Yes</span> : <span className="badge draft">No</span>}</td>
                  <td>{t.clicked ? <span className="badge click">Yes</span> : <span className="badge draft">No</span>}</td>
                  <td>{t.reported ? <span className="badge active">Yes</span> : <span className="badge draft">No</span>}</td>
                  <td>{t.training_completed ? <span className="badge active">Done</span> : <span className="badge draft">Pending</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}