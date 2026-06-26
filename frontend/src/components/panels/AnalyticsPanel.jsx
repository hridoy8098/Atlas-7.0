// AnalyticsPanel.jsx
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'
import useAtlasStore from '../../store/useAtlasStore'

const mockData = [
  { name: 'Mon', productivity: 75, focus: 68 },
  { name: 'Tue', productivity: 82, focus: 74 },
  { name: 'Wed', productivity: 70, focus: 60 },
  { name: 'Thu', productivity: 88, focus: 85 },
  { name: 'Fri', productivity: 91, focus: 88 },
  { name: 'Sat', productivity: 65, focus: 55 },
  { name: 'Sun', productivity: 78, focus: 72 },
]

export default function AnalyticsPanel() {
  return (
    <div style={{ display: 'grid', gridTemplateRows: 'auto 1fr', gap: 12, height: '100%' }}>
      {/* Score cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 }}>
        {[
          { label: 'Productivity', value: '87', unit: '%', color: '#00ffc8' },
          { label: 'Focus Score', value: '72', unit: '%', color: '#00aaff' },
          { label: 'Study Hours', value: '4.5', unit: 'h', color: '#ff88ff' },
          { label: 'Habit Streak', value: '12', unit: 'd', color: '#ffaa00' },
        ].map(c => (
          <div key={c.label} style={S.card}>
            <div style={{ fontSize: 9, color: 'var(--text-dim)', letterSpacing: 2, marginBottom: 8 }}>{c.label.toUpperCase()}</div>
            <div style={{ fontFamily: 'Share Tech Mono', fontSize: 32, color: c.color }}>{c.value}<span style={{ fontSize: 14 }}>{c.unit}</span></div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div style={S.card}>
        <div style={{ fontFamily: 'Orbitron', fontSize: 9, color: 'var(--text-dim)', letterSpacing: 2, marginBottom: 16 }}>WEEKLY PERFORMANCE</div>
        <ResponsiveContainer width="100%" height="85%">
          <LineChart data={mockData}>
            <XAxis dataKey="name" tick={{ fill: 'rgba(0,255,200,0.5)', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis domain={[0,100]} tick={{ fill: 'rgba(0,255,200,0.5)', fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: '#001020', border: '1px solid rgba(0,255,200,0.3)', borderRadius: 8, color: '#00ffc8' }} />
            <Line type="monotone" dataKey="productivity" stroke="#00ffc8" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="focus" stroke="#00aaff" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

const S = {
  card: { background: 'rgba(0,20,16,0.7)', border: '1px solid rgba(0,255,200,0.15)', borderRadius: 10, padding: 14 },
}
