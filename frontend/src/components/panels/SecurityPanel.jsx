import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Eye, Wifi, Lock, Key, Bug } from 'lucide-react'

export default function SecurityPanel() {
  const [activeTab, setActiveTab] = useState('overview')
  const [scanning, setScanning] = useState(false)
  const [scanResult, setScanResult] = useState(null)
  const [networkStatus, setNetworkStatus] = useState({ active: false, ip: '192.168.0.101', threats: 0 })
  const [breachChecked, setBreachChecked] = useState(false)

  const runScan = async () => {
    setScanning(true)
    setScanResult(null)
    await new Promise(r => setTimeout(r, 2000))
    setScanResult({ threats: 0, files: 1243, time: '2.1s' })
    setScanning(false)
  }

  const runBreachCheck = async () => {
    setBreachChecked(false)
    await new Promise(r => setTimeout(r, 1500))
    setBreachChecked(true)
  }

  const tabs = [
    { id: 'overview', label: 'OVERVIEW', icon: Shield },
    { id: 'scan', label: 'MALWARE SCAN', icon: Bug },
    { id: 'network', label: 'NETWORK', icon: Wifi },
    { id: 'privacy', label: 'PRIVACY', icon: Eye },
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
          <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} style={S.grid3}>
            <div style={S.card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Shield size={18} color="#00ffc8" />
                <span style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2 }}>PROTECTION</span>
              </div>
              <div style={{ fontFamily: 'Share Tech Mono', fontSize: 28, color: '#00ffc8' }}>ACTIVE</div>
              <div style={{ fontSize: 11, color: 'rgba(0,255,200,0.5)', marginTop: 4 }}>Real-time protection on</div>
            </div>

            <div style={S.card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Lock size={18} color="#00aaff" />
                <span style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2 }}>AUTH</span>
              </div>
              <div style={{ fontFamily: 'Share Tech Mono', fontSize: 28, color: '#00aaff' }}>2FA</div>
              <div style={{ fontSize: 11, color: 'rgba(0,170,255,0.5)', marginTop: 4 }}>Two-factor active</div>
            </div>

            <div style={S.card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Key size={18} color="#ff88ff" />
                <span style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2 }}>PASSWORDS</span>
              </div>
              <div style={{ fontFamily: 'Share Tech Mono', fontSize: 28, color: '#ff88ff' }}>24</div>
              <div style={{ fontSize: 11, color: 'rgba(255,136,255,0.5)', marginTop: 4 }}>Passwords stored</div>
            </div>

            <div style={S.card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Wifi size={18} color="#ffaa00" />
                <span style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2 }}>NETWORK</span>
              </div>
              <div style={{ fontFamily: 'Share Tech Mono', fontSize: 28, color: networkStatus.threats > 0 ? '#ff5533' : '#00ff88' }}>
                {networkStatus.threats > 0 ? `${networkStatus.threats} THREATS` : 'SECURE'}
              </div>
              <div style={{ fontSize: 11, color: 'rgba(0,255,200,0.5)', marginTop: 4 }}>{networkStatus.ip}</div>
            </div>

            <div style={S.card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Bug size={18} color="#ff5533" />
                <span style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2 }}>LAST SCAN</span>
              </div>
              <div style={{ fontFamily: 'Share Tech Mono', fontSize: 20, color: '#ff5533' }}>
                {scanResult ? `${scanResult.threats} threats` : 'No scan yet'}
              </div>
              <div style={{ fontSize: 11, color: 'rgba(0,255,200,0.5)', marginTop: 4 }}>
                {scanResult ? `${scanResult.files} files in ${scanResult.time}` : 'Run a scan to check'}
              </div>
            </div>

            <div style={S.card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Eye size={18} color="#ff6600" />
                <span style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2 }}>BREACH CHECK</span>
              </div>
              <div style={{ fontFamily: 'Share Tech Mono', fontSize: 20, color: breachChecked ? '#00ff88' : '#ffaa00' }}>
                {breachChecked ? 'NO BREACHES' : 'NOT CHECKED'}
              </div>
              <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                onClick={runBreachCheck} style={{ ...S.smallBtn, marginTop: 8 }}>
                Check Now
              </motion.button>
            </div>
          </motion.div>
        )}

        {activeTab === 'scan' && (
          <motion.div key="scan" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 20, height: '100%' }}>
            <div style={S.scanCircle}>
              {scanning ? (
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  style={{ width: 60, height: 60, borderRadius: '50%', border: '3px solid transparent', borderTopColor: '#00ffc8', borderRightColor: '#00aaff' }} />
              ) : scanResult ? (
                <div style={{ fontFamily: 'Orbitron', fontSize: 14, color: scanResult.threats === 0 ? '#00ff88' : '#ff5533' }}>
                  {scanResult.threats === 0 ? 'CLEAN' : `${scanResult.threats} THREATS`}
                </div>
              ) : (
                <Bug size={32} color="var(--text-dim)" />
              )}
            </div>
            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              onClick={runScan} disabled={scanning}
              style={{ ...S.scanBtn, opacity: scanning ? 0.5 : 1 }}>
              {scanning ? 'SCANNING...' : scanResult ? 'SCAN AGAIN' : 'START SCAN'}
            </motion.button>
            {scanResult && (
              <div style={{ display: 'flex', gap: 24 }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'Share Tech Mono', fontSize: 22, color: '#00ffc8' }}>{scanResult.files}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>FILES</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'Share Tech Mono', fontSize: 22, color: '#00ffc8' }}>{scanResult.time}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>DURATION</div>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'network' && (
          <motion.div key="network" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, height: '100%' }}>
            <div style={S.card}>
              <div style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2, marginBottom: 12 }}>NETWORK STATUS</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#00ff88', boxShadow: '0 0 8px #00ff88' }} />
                <span style={{ fontFamily: 'Share Tech Mono', fontSize: 16, color: '#00ff88' }}>CONNECTED</span>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 4 }}>IP: {networkStatus.ip}</div>
            </div>
            <div style={S.card}>
              <div style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2, marginBottom: 12 }}>CONNECTIONS</div>
              <div style={{ fontFamily: 'Share Tech Mono', fontSize: 22, color: '#00aaff' }}>7</div>
              <div style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 4 }}>Active connections</div>
            </div>
          </motion.div>
        )}

        {activeTab === 'privacy' && (
          <motion.div key="privacy" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', gap: 10, height: '100%' }}>
            {[
              { label: 'PRIVACY MODE', desc: 'Block tracking and data collection', active: true },
              { label: 'SCREEN WATERMARK', desc: 'Overlay user info on screen', active: false },
              { label: 'SELF DESTRUCT', desc: 'Auto-wipe data on intrusion', active: false },
              { label: 'AUTO-LOCK ON IDLE', desc: 'Lock after 5 min inactivity', active: true },
            ].map((item, i) => (
              <div key={i} style={S.card}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--cyan)', letterSpacing: 1, marginBottom: 4 }}>{item.label}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>{item.desc}</div>
                  </div>
                  <div style={{
                    width: 44, height: 24, borderRadius: 12, cursor: 'pointer',
                    background: item.active ? 'rgba(0,255,200,0.3)' : 'rgba(255,255,255,0.1)',
                    position: 'relative', transition: 'background 0.3s',
                    border: `1px solid ${item.active ? 'rgba(0,255,200,0.5)' : 'transparent'}`
                  }}>
                    <motion.div animate={{ x: item.active ? 22 : 2 }}
                      style={{ width: 18, height: 18, borderRadius: '50%', background: item.active ? '#00ffc8' : '#666', marginTop: 2 }} />
                  </div>
                </div>
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
  card: { background: 'rgba(0,20,16,0.7)', border: '1px solid rgba(0,255,200,0.15)', borderRadius: 10, padding: 14 },
  grid3: { display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10 },
  smallBtn: { padding: '6px 16px', borderRadius: 6, border: '1px solid rgba(0,255,200,0.3)', background: 'rgba(0,255,200,0.08)', color: 'var(--cyan)', fontFamily: 'Rajdhani', fontSize: 12, cursor: 'pointer' },
  scanCircle: { width: 120, height: 120, borderRadius: '50%', border: '2px solid rgba(0,255,200,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,20,16,0.7)' },
  scanBtn: { padding: '12px 32px', borderRadius: 8, border: '1px solid rgba(0,255,200,0.3)', background: 'rgba(0,255,200,0.1)', color: 'var(--cyan)', fontFamily: 'Orbitron', fontSize: 11, letterSpacing: 3, cursor: 'pointer' },
}
