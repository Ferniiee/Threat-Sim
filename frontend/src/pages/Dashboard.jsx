import { useState } from 'react'
import Campaigns from '../components/Campaigns'
import NewCampaign from '../components/NewCampaign'
import CampaignDetail from '../components/CampaignDetail'

export default function Dashboard({ onLogout }) {
  const [page, setPage] = useState('campaigns')
  const [selectedCampaign, setSelectedCampaign] = useState(null)

  const navigate = (p, data = null) => {
    setPage(p)
    if (data) setSelectedCampaign(data)
  }

  return (
    <div>
      <div className="sidebar">
        <h1>ThreatSim</h1>
        <p>Security Awareness Platform</p>
        <button
          className={`nav-item ${page === 'campaigns' ? 'active' : ''}`}
          onClick={() => navigate('campaigns')}
        >
          Campaigns
        </button>
        <button
          className={`nav-item ${page === 'new' ? 'active' : ''}`}
          onClick={() => navigate('new')}
        >
          New Campaign
        </button>
        <button
          className="nav-item"
          style={{position: 'absolute', bottom: '24px', color: '#ef4444'}}
          onClick={onLogout}
        >
          Sign Out
        </button>
      </div>
      <div className="main">
        {page === 'campaigns' && (
          <Campaigns onSelect={(c) => navigate('detail', c)} />
        )}
        {page === 'new' && (
          <NewCampaign onCreated={() => navigate('campaigns')} />
        )}
        {page === 'detail' && selectedCampaign && (
          <CampaignDetail campaign={selectedCampaign} onBack={() => navigate('campaigns')} />
        )}
      </div>
    </div>
  )
}