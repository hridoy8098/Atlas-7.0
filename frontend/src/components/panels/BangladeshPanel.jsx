import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Globe, Newspaper, TrendingUp, Landmark } from 'lucide-react'

const divisions = [
  { name: 'Dhaka', area: 'পৃথক', pop: '২.৩ কোটি' },
  { name: 'Chittagong', area: 'পৃথক', pop: '৩.৩ কোটি' },
  { name: 'Rajshahi', area: 'পৃথক', pop: '২.০ কোটি' },
  { name: 'Khulna', area: 'পৃথক', pop: '১.৭ কোটি' },
  { name: 'Barisal', area: 'পৃথক', pop: '৯০ লক্ষ' },
  { name: 'Sylhet', area: 'পৃথক', pop: '১.১ কোটি' },
  { name: 'Rangpur', area: 'পৃথক', pop: '১.৮ কোটি' },
  { name: 'Mymensingh', area: 'পৃথক', pop: '১.২ কোটি' },
]

const newsItems = [
  { headline: 'বাংলাদেশের অর্থনীতি চাঙ্গা হচ্ছে', source: 'Daily Star', time: '২ ঘণ্টা আগে' },
  { headline: 'ঢাকা স্টক এক্সচেঞ্জে রেকর্ড লেনদেন', source: 'Financial Express', time: '৩ ঘণ্টা আগে' },
  { headline: 'আইটি খাতে রপ্তানি আয় বেড়েছে ২০%', source: 'Business Standard', time: '৫ ঘণ্টা আগে' },
  { headline: 'নতুন এলএনজি টার্মিনাল চালু', source: 'Dhaka Tribune', time: '৮ ঘণ্টা আগে' },
]

const districts = [
  { name: 'Dhaka', bn: 'ঢাকা', desc: 'জাতীয় রাজধানী, ২৩০০ বছর পুরনো' },
  { name: 'Sylhet', bn: 'সিলেট', desc: 'চা বাগান ও প্রাকৃতিক সৌন্দর্যের দেশ' },
  { name: 'Cox\'s Bazar', bn: 'কক্সবাজার', desc: 'বিশ্বের দীর্ঘতম সমুদ্র সৈকত (১২০ কিমি)' },
  { name: 'Sundarbans', bn: 'সুন্দরবন', desc: 'বিশ্বের বৃহত্তম ম্যানগ্রোভ বন' },
]

export default function BangladeshPanel() {
  const [activeTab, setActiveTab] = useState('overview')

  const tabs = [
    { id: 'overview', label: 'OVERVIEW', icon: Globe },
    { id: 'news', label: 'NEWS', icon: Newspaper },
    { id: 'economy', label: 'ECONOMY', icon: TrendingUp },
    { id: 'divisions', label: 'DIVISIONS', icon: Landmark },
  ]

  return (
    <div style={{ display: 'grid', gridTemplateRows: 'auto 1fr', gap: 12, height: '100%' }}>
      <div style={{ display: 'flex', gap: 6 }}>
        {tabs.map(tab => (
          <motion.button key={tab.id} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...S.tab,
              background: activeTab === tab.id ? 'rgba(0,255,200,0.1)' : 'transparent',
              borderColor: activeTab === tab.id ? 'rgba(0,255,200,0.4)' : 'rgba(0,255,200,0.12)',
              color: activeTab === tab.id ? 'var(--cyan)' : 'var(--text-dim)',
            }}>
            <tab.icon size={14} />
            <span style={{ fontSize: 10, letterSpacing: 1 }}>{tab.label}</span>
          </motion.button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 10, height: '100%' }}>
            <div style={S.mainCard}>
              <div style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2, marginBottom: 12 }}>
                🇧🇩 BANGLADESH
              </div>
              <div style={{ fontFamily: 'Share Tech Mono', fontSize: 22, color: 'var(--cyan)', marginBottom: 4 }}>গণপ্রজাতন্ত্রী বাংলাদেশ</div>
              <div style={{ fontSize: 12, color: 'rgba(0,255,200,0.6)' }}>People's Republic of Bangladesh</div>
              <div style={{ display: 'flex', gap: 24, marginTop: 16 }}>
                <div><div style={{ fontFamily: 'Share Tech Mono', fontSize: 18, color: '#00ffc8' }}>১৭.৪ কোটি</div><div style={{ fontSize: 9, color: 'var(--text-dim)' }}>জনসংখ্যা</div></div>
                <div><div style={{ fontFamily: 'Share Tech Mono', fontSize: 18, color: '#00aaff' }}>১,৪৭,৫৭০ km²</div><div style={{ fontSize: 9, color: 'var(--text-dim)' }}>আয়তন</div></div>
              </div>
              <div style={{ display: 'flex', gap: 24, marginTop: 10 }}>
                <div><div style={{ fontFamily: 'Share Tech Mono', fontSize: 18, color: '#ff88ff' }}>ঢাকা</div><div style={{ fontSize: 9, color: 'var(--text-dim)' }}>রাজধানী</div></div>
                  <div><div style={{ fontFamily: 'Share Tech Mono', fontSize: 18, color: '#ffaa00' }}>বাংলা</div><div style={{ fontSize: 9, color: 'var(--text-dim)' }}>জাতীয় ভাষা</div></div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {districts.map((d, i) => (
                <div key={i} style={S.card}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontFamily: 'Orbitron', fontSize: 11, color: 'var(--cyan)', letterSpacing: 1 }}>{d.name}</span>
                    <span style={{ fontSize: 11, color: 'rgba(0,255,200,0.5)' }}>{d.bn}</span>
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>{d.desc}</div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'news' && (
          <motion.div key="news" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', gap: 8, height: '100%', overflow: 'auto' }}>
            {newsItems.map((item, i) => (
              <div key={i} style={S.card}>
                <div style={{ fontFamily: 'Rajdhani', fontSize: 14, color: '#e0f0e8', marginBottom: 6, fontWeight: 600 }}>{item.headline}</div>
                <div style={{ display: 'flex', gap: 12 }}>
                  <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>{item.source}</span>
                  <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>{item.time}</span>
                </div>
              </div>
            ))}
            <div style={{ padding: 12, textAlign: 'center', color: 'var(--text-dim)', fontSize: 10 }}>
              Real-time news API coming soon
            </div>
          </motion.div>
        )}

        {activeTab === 'economy' && (
          <motion.div key="economy" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 10, height: '100%' }}>
            {[
              { label: 'GDP Growth', value: '6.5%', color: '#00ffc8' },
              { label: 'Inflation', value: '4.2%', color: '#ffaa00' },
              { label: 'USD Rate', value: '১০৮৳', color: '#00aaff' },
              { label: 'Remittance', value: '$২.৪B', color: '#ff88ff' },
              { label: 'Stock (DSEX)', value: '৬,৩২০', color: '#ff6600' },
              { label: 'Export', value: '$৫.৬B', color: '#00ff88' },
            ].map((econ, i) => (
              <div key={i} style={S.card}>
                <div style={{ fontFamily: 'Orbitron', fontSize: 9, color: 'var(--text-dim)', letterSpacing: 2, marginBottom: 8 }}>{econ.label}</div>
                <div style={{ fontFamily: 'Share Tech Mono', fontSize: 24, color: econ.color }}>{econ.value}</div>
              </div>
            ))}
          </motion.div>
        )}

        {activeTab === 'divisions' && (
          <motion.div key="divisions" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 8, height: '100%' }}>
            {divisions.map((div, i) => (
              <div key={i} style={S.card}>
                <div style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--cyan)', letterSpacing: 1, marginBottom: 4 }}>{div.name}</div>
                <div style={{ fontSize: 11, color: 'rgba(0,255,200,0.6)' }}>{div.pop}</div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

const S = {
  tab: { display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderRadius: 8, border: '1px solid', cursor: 'pointer', fontFamily: 'Rajdhani', fontSize: 12, background: 'transparent' },
  card: { background: 'rgba(0,20,16,0.7)', border: '1px solid rgba(0,255,200,0.15)', borderRadius: 10, padding: 12 },
  mainCard: { background: 'rgba(0,20,16,0.7)', border: '1px solid rgba(0,255,200,0.15)', borderRadius: 10, padding: 16, display: 'flex', flexDirection: 'column' },
}
