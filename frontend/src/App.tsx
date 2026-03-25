import { useState, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import 'bootstrap/dist/css/bootstrap.min.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [summonerName, setSummonerName] = useState('')
  const [region, setRegion] = useState('na1')
  const [matches, setMatches] = useState<any[]>([])
  const [coachingAdvice, setCoachingAdvice] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [theme, setTheme] = useState<'light'|'dark'>('dark')
  const [gameType, setGameType] = useState('ALL')

  useEffect(() => {
    document.documentElement.setAttribute('data-bs-theme', theme);
  }, [theme])

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark')

  const fetchMatches = async () => {
    if (!summonerName.includes('#')) {
      setError('Please include the tagline (e.g., Name#Tag)')
      return
    }
    setLoading(true)
    setError('')
    setCoachingAdvice('')
    try {
      const res = await axios.get(`${API_BASE}/api/matches`, {
        params: { summoner: summonerName, region, gameType }
      })
      if (res.data && res.data.recent_matches) {
        setMatches(res.data.recent_matches)
        if (res.data.recent_matches.length === 0) {
          setError('This player hasn\'t played any matches recently. Cannot perform AI analysis.');
        }
      } else {
        setError('No matches found.')
      }
    } catch (err: any) {
      console.error("Fetch Matches Error:", err);
      setError('Oops! We couldn\'t find that player. Please check the summoner name, tagline, and server region and try again.');
    } finally {
      setLoading(false)
    }
  }

  const getCoaching = async () => {
    if (matches.length === 0) return
    setLoading(true)
    setError('')
    try {
      const res = await axios.post(`${API_BASE}/api/coach`, {
        summoner_name: summonerName,
        match_data: matches,
        game_type: gameType
      })
      if (res.data && res.data.advice) {
        setCoachingAdvice(res.data.advice)
      } else {
        setError('No advice returned.')
      }
    } catch (err: any) {
      console.error("Coaching Analysis Error:", err);
      setError('Uh oh! The AI coach is currently taking a break. Please try your analysis again later.');
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container py-5 d-flex flex-column align-items-center min-vh-100 position-relative">
      <button 
        onClick={toggleTheme}
        className={`btn position-absolute top-0 end-0 mt-3 me-3 ${theme === 'dark' ? 'btn-outline-light' : 'btn-outline-dark'}`}
      >
        {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
      </button>

      <h1 className="display-4 fw-bolder text-gradient-cyan-blue mb-5 text-center px-3 drop-shadow-sm">
        Gaming Coach AI
      </h1>
      
      <div className="w-100 gamer-card" style={{ maxWidth: '800px' }}>
        <label className="form-label text-uppercase fw-bold text-muted small mb-2">Summoner Name (Name#Tag)</label>
        <div className="d-flex flex-wrap gap-3 mb-3 justify-content-center">
          <input 
            type="text" 
            value={summonerName}
            onChange={(e) => setSummonerName(e.target.value)}
            className="form-control form-control-lg gamer-input flex-grow-1"
            placeholder="Faker#KR1"
            style={{ minWidth: '220px' }}
          />
          <select 
            value={region} 
            onChange={e => setRegion(e.target.value)}
            className="form-select form-select-lg gamer-input"
            style={{ width: 'auto' }}
          >
            <option value="na1">North America (NA)</option>
            <option value="euw1">Europe West (EUW)</option>
            <option value="eun1">Europe Nordic/East (EUNE)</option>
            <option value="kr">Korea (KR)</option>
            <option value="sg2">Singapore/Malaysia (SG2)</option>
            <option value="ph2">Philippines (PH2)</option>
            <option value="tw2">Taiwan/HK/Macao (TW2)</option>
            <option value="vn2">Vietnam (VN2)</option>
            <option value="th2">Thailand (TH2)</option>
            <option value="jp1">Japan (JP)</option>
            <option value="br1">Brazil (BR)</option>
            <option value="la1">Latin America N. (LAN)</option>
            <option value="la2">Latin America S. (LAS)</option>
            <option value="oc1">Oceania (OCE)</option>
          </select>
          <select 
            value={gameType} 
            onChange={e => setGameType(e.target.value)}
            className="form-select form-select-lg gamer-input"
            style={{ width: 'auto' }}
          >
            <option value="ALL">All Modes</option>
            <option value="RANKED">Ranked</option>
            <option value="UNRANKED_SR">Unranked Summoner's Rift</option>
            <option value="EVENT">Event Mode (URF, etc)</option>
            <option value="ARAM">ARAM</option>
            <option value="AAA_ARAM">AAA ARAM</option>
          </select>
        </div>
        
        {error && (
          <div className="alert mt-4 d-flex align-items-center mb-0 border-0 shadow-sm" style={{ backgroundColor: 'rgba(220, 53, 69, 0.15)', color: '#ff8796', borderRadius: '0.75rem' }} role="alert">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" className="bi bi-exclamation-triangle-fill flex-shrink-0 me-3" viewBox="0 0 16 16" role="img" aria-label="Warning:">
              <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
            </svg>
            <div className="fw-medium">
              {error}
            </div>
          </div>
        )}

        <button 
          onClick={fetchMatches}
          disabled={loading}
          className="btn gamer-btn-cyan w-100 py-3 mt-4"
        >
          {loading && !matches.length && !coachingAdvice ? (
            <span><span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Fetching Data...</span>
          ) : 'Fetch Matches'}
        </button>
      </div>

      {matches.length > 0 && !coachingAdvice && (
        <div className="w-100 mt-5 animate-fade-in" style={{ maxWidth: '800px' }}>
          <h3 className="h4 fw-bold mb-4" style={{ color: 'var(--text-primary)' }}>Recent Matches</h3>
          <div className="d-flex flex-column gap-3">
            {matches.map((m, i) => (
              <div key={i} className="match-item d-flex flex-column gap-2 p-3">
                <div className="d-flex justify-content-between align-items-center">
                  <div className="d-flex align-items-center">
                    <div className={`indicator ${m.win ? 'indicator-win' : 'indicator-loss'}`}></div>
                    <div>
                      <div className="fs-5 fw-bold" style={{ color: 'var(--text-primary)' }}>
                        {m.championName} {m.role && m.role !== "Invalid" && <span className="small ms-1" style={{ color: 'var(--text-muted)' }}>({m.role})</span>}
                      </div>
                      <div className="small fw-medium mt-1 d-flex gap-3 flex-wrap" style={{ color: 'var(--text-muted)' }}>
                        <span>KDA: {m.kills}/{m.deaths}/{m.assists}</span>
                        { ['ARAM', 'AAA ARAM'].includes(m.gameMode) ? (
                          <>
                            <span>Dmg%: {m.damagePct}%</span>
                            <span>KP: {m.killParticipation}%</span>
                            <span>Dmg/Gold: {m.damagePerGold}</span>
                          </>
                        ) : (
                          <>
                            <span>CS/m: {m.csPerMin}</span>
                            <span className={m.goldDiff15 > 0 ? 'text-success' : m.goldDiff15 < 0 ? 'text-danger' : ''}>
                              GD@15: {m.goldDiff15 > 0 ? '+' : ''}{m.goldDiff15}
                            </span>
                            <span>VS: {m.visionScore}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-end">
                    <div className={m.win ? 'text-win' : 'text-loss'}>{m.win ? 'Victory' : 'Defeat'}</div>
                    <div className="small text-muted mt-1">{m.gameMode}</div>
                  </div>
                </div>

                {m.detailed_analysis_metrics && (
                  <div className="mt-3 p-3 rounded" style={{ background: 'rgba(0,0,0,0.2)', fontSize: '0.85rem' }}>
                    <div className="d-flex justify-content-between mb-2">
                      <span><strong>Objective Dmg:</strong> {m.detailed_analysis_metrics.damageDealtToObjectives}</span>
                      <span><strong>Turret Dmg:</strong> {m.detailed_analysis_metrics.damageDealtToTurrets}</span>
                      <span><strong>CC Time:</strong> {m.detailed_analysis_metrics.timeCCingOthers}s</span>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span><strong>Solo Kills:</strong> {m.detailed_analysis_metrics.challenges?.soloKills || 0}</span>
                      <span><strong>Lane Adv %:</strong> {m.detailed_analysis_metrics.challenges?.laningPhaseGoldExpAdvantage ? Math.round(m.detailed_analysis_metrics.challenges.laningPhaseGoldExpAdvantage * 100) : 0}%</span>
                      <span><strong>Skirmishes Won:</strong> {m.detailed_analysis_metrics.challenges?.skirmishClashWon || 0}</span>
                    </div>
                    {m.goldDiffOverTime && m.goldDiffOverTime.length > 0 && (
                      <div className="mt-3 bg-dark rounded p-2" style={{ height: '140px', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <h6 className="text-center small mb-2" style={{ color: 'var(--text-muted)' }}>Gold Difference Timeline vs Opponent</h6>
                        <ResponsiveContainer width="100%" height="80%">
                          <LineChart data={m.goldDiffOverTime} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <XAxis dataKey="minute" hide={true} />
                            <YAxis hide={true} domain={['dataMin', 'dataMax']} />
                            <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333', borderRadius: '8px' }} labelStyle={{ display: 'none' }} itemStyle={{ color: '#fff' }} formatter={(val: any) => [`${val > 0 ? '+' : ''}${val} Gold`, 'Gold Diff']} />
                            <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
                            <Line type="monotone" dataKey="goldDiff" stroke={m.goldDiff15 >= 0 ? "#198754" : "#dc3545"} strokeWidth={2} dot={false} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
          
          <button 
            onClick={getCoaching}
            disabled={loading}
            className="btn gamer-btn-purple w-100 py-3 mt-4"
          >
             {loading ? (
              <span><span className="spinner-border spinner-border-sm me-2"></span>Analyzing with AI...</span>
            ) : 'Get AI Coaching Advice ✨'}
          </button>
        </div>
      )}

      {coachingAdvice && (
        <div className="w-100 coaching-markdown animate-fade-in" style={{ maxWidth: '800px' }}>
          <div className="border-bottom border-dark pb-3 mb-4">
            <h2 className="text-gradient-purple-pink fw-bolder m-0">
              Coaching Analysis
            </h2>
            <p className="text-muted small mt-2 m-0">Analysis generated by Gemini 2.5 Flash</p>
          </div>
          
          <div className="text-start" style={{ color: 'var(--text-primary)' }}>
            <ReactMarkdown>{coachingAdvice}</ReactMarkdown>
          </div>
          
          <button 
            onClick={() => { setCoachingAdvice(''); setMatches([]) }}
            className="btn btn-outline-secondary mt-5"
          >
            Analyze another player
          </button>
        </div>
      )}
    </div>
  )
}

export default App
