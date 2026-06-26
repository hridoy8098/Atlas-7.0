import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BookOpen, Timer, Notebook, FileText, Sparkles } from 'lucide-react'

const flashcards = [
  { front: 'React State Management', back: 'UseState, UseReducer, Context, Zustand, Redux' },
  { front: 'Python Decorators', back: '@decorator — functions that modify other functions' },
  { front: 'Docker Container', back: 'Lightweight VM — runs isolated apps with own FS' },
  { front: 'REST API', back: 'GET, POST, PUT, DELETE — stateless client-server' },
]

const pomodoros = [
  { label: 'FOCUS', duration: 25, color: '#00ffc8' },
  { label: 'BREAK', duration: 5, color: '#00aaff' },
]

export default function StudyPanel() {
  const [activeTab, setActiveTab] = useState('pomodoro')
  const [flipIndex, setFlipIndex] = useState(null)
  const [currentCard, setCurrentCard] = useState(0)

  // Pomodoro
  const [pomoRunning, setPomoRunning] = useState(false)
  const [pomoMode, setPomoMode] = useState(0)
  const [secondsLeft, setSecondsLeft] = useState(pomodoros[0].duration * 60)
  const pomoRef = useRef(null)

  useEffect(() => {
    if (pomoRunning) {
      pomoRef.current = setInterval(() => {
        setSecondsLeft(s => {
          if (s <= 1) {
            clearInterval(pomoRef.current)
            setPomoRunning(false)
            return 0
          }
          return s - 1
        })
      }, 1000)
    }
    return () => clearInterval(pomoRef.current)
  }, [pomoRunning])

  const startPomo = () => {
    if (secondsLeft === 0) {
      setSecondsLeft(pomodoros[pomoMode].duration * 60)
    }
    setPomoRunning(true)
  }

  const resetPomo = () => {
    clearInterval(pomoRef.current)
    setPomoRunning(false)
    setSecondsLeft(pomodoros[pomoMode].duration * 60)
  }

  const switchPomoMode = (idx) => {
    clearInterval(pomoRef.current)
    setPomoRunning(false)
    setPomoMode(idx)
    setSecondsLeft(pomodoros[idx].duration * 60)
  }

  const formatTime = (s) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  }

  const tabs = [
    { id: 'pomodoro', label: 'POMODORO', icon: Timer },
    { id: 'flashcards', label: 'FLASHCARDS', icon: BookOpen },
    { id: 'notes', label: 'NOTES', icon: Notebook },
    { id: 'papers', label: 'PAST PAPERS', icon: FileText },
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
        {activeTab === 'pomodoro' && (
          <motion.div key="pomodoro" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 20, height: '100%' }}>
            <div style={{ display: 'flex', gap: 8 }}>
              {pomodoros.map((p, i) => (
                <motion.button key={p.label} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => switchPomoMode(i)}
                  style={{
                    ...S.modeBtn,
                    background: pomoMode === i ? `${p.color}22` : 'transparent',
                    borderColor: pomoMode === i ? p.color : 'rgba(0,255,200,0.15)',
                    color: pomoMode === i ? p.color : 'var(--text-dim)',
                  }}>
                  {p.label} · {p.duration}m
                </motion.button>
              ))}
            </div>

            <div style={{ position: 'relative', width: 180, height: 180 }}>
              <svg width="180" height="180" style={{ transform: 'rotate(-90deg)' }}>
                <circle cx="90" cy="90" r="78" fill="none" stroke="rgba(0,255,200,0.1)" strokeWidth="6" />
                <motion.circle cx="90" cy="90" r="78" fill="none"
                  stroke={pomodoros[pomoMode].color} strokeWidth="6" strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 78}
                  strokeDashoffset={2 * Math.PI * 78 * (1 - secondsLeft / (pomodoros[pomoMode].duration * 60))}
                  style={{ transition: 'stroke-dashoffset 1s linear' }} />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ fontFamily: 'Share Tech Mono', fontSize: 38, color: pomodoros[pomoMode].color }}>{formatTime(secondsLeft)}</div>
                <div style={{ fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2, marginTop: 4 }}>{pomodoros[pomoMode].label}</div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              {!pomoRunning ? (
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={startPomo} style={S.pomoBtn}>
                  {secondsLeft === 0 ? 'RESTART' : 'START'}
                </motion.button>
              ) : (
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => setPomoRunning(false)} style={{ ...S.pomoBtn, background: 'rgba(255,50,50,0.15)', borderColor: 'rgba(255,50,50,0.4)', color: '#ff6666' }}>
                  PAUSE
                </motion.button>
              )}
              <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                onClick={resetPomo} style={{ ...S.pomoBtn, background: 'rgba(255,255,255,0.05)', borderColor: 'rgba(0,255,200,0.15)', color: 'var(--text-dim)' }}>
                RESET
              </motion.button>
            </div>
          </motion.div>
        )}

        {activeTab === 'flashcards' && (
          <motion.div key="flashcards" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, height: '100%' }}>
            <div style={{ position: 'relative', width: '100%', maxWidth: 420, height: 200, perspective: 1000 }}
              onClick={() => setFlipIndex(flipIndex === currentCard ? null : currentCard)}>
              <motion.div
                animate={{ rotateY: flipIndex === currentCard ? 180 : 0 }}
                transition={{ duration: 0.5 }}
                style={{ width: '100%', height: '100%', transformStyle: 'preserve-3d', cursor: 'pointer', position: 'relative' }}>
                <div style={{ ...S.cardFace, backfaceVisibility: 'hidden', background: 'rgba(0,25,20,0.85)', border: '1px solid rgba(0,255,200,0.25)' }}>
                  <div style={{ fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2, marginBottom: 16 }}>QUESTION</div>
                  <div style={{ fontFamily: 'Orbitron', fontSize: 14, color: 'var(--cyan)', lineHeight: 1.5 }}>{flashcards[currentCard].front}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 'auto', letterSpacing: 1 }}>Click to reveal</div>
                </div>
                <div style={{ ...S.cardFace, backfaceVisibility: 'hidden', transform: 'rotateY(180deg)', background: 'rgba(10,0,30,0.9)', border: '1px solid rgba(150,50,255,0.3)' }}>
                  <div style={{ fontSize: 10, color: '#aa66ff', letterSpacing: 2, marginBottom: 16 }}>ANSWER</div>
                  <div style={{ fontSize: 14, color: '#cc88ff', lineHeight: 1.6 }}>{flashcards[currentCard].back}</div>
                </div>
              </motion.div>
            </div>

            <div style={{ display: 'flex', gap: 8 }}>
              <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                onClick={() => { setFlipIndex(null); setCurrentCard(i => (i - 1 + flashcards.length) % flashcards.length) }}
                style={S.cardNav}>◀ PREV</motion.button>
              <span style={{ fontSize: 11, color: 'var(--text-dim)', alignSelf: 'center' }}>
                {currentCard + 1} / {flashcards.length}
              </span>
              <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                onClick={() => { setFlipIndex(null); setCurrentCard(i => (i + 1) % flashcards.length) }}
                style={S.cardNav}>NEXT ▶</motion.button>
            </div>
          </motion.div>
        )}

        {activeTab === 'notes' && (
          <motion.div key="notes" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10, height: '100%' }}>
            {[
              { title: 'AI & ML', color: '#00ffc8', items: 12 },
              { title: 'Web Dev', color: '#00aaff', items: 8 },
              { title: 'Cybersecurity', color: '#ff88ff', items: 6 },
              { title: 'Bangladesh Studies', color: '#ff6600', items: 10 },
              { title: 'Programming', color: '#ffaa00', items: 15 },
              { title: 'Math & Logic', color: '#ff5533', items: 7 },
            ].map((n, i) => (
              <div key={i} style={S.card}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <Sparkles size={14} color={n.color} />
                  <span style={{ fontFamily: 'Orbitron', fontSize: 10, color: n.color, letterSpacing: 1 }}>{n.title}</span>
                </div>
                <div style={{ fontFamily: 'Share Tech Mono', fontSize: 24, color: n.color }}>{n.items}</div>
                <div style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 4 }}>Notes</div>
              </div>
            ))}
          </motion.div>
        )}

        {activeTab === 'papers' && (
          <motion.div key="papers" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', gap: 8, height: '100%' }}>
            {[
              { subject: 'Computer Science', year: '2024', board: 'Dhaka Board' },
              { subject: 'Physics', year: '2024', board: 'Rajshahi Board' },
              { subject: 'Mathematics', year: '2023', board: 'Chittagong Board' },
              { subject: 'English', year: '2024', board: 'National' },
            ].map((p, i) => (
              <div key={i} style={{ ...S.card, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontFamily: 'Orbitron', fontSize: 11, color: 'var(--cyan)', letterSpacing: 1 }}>{p.subject}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 2 }}>{p.board} · {p.year}</div>
                </div>
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  style={S.smallBtn}>OPEN</motion.button>
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
  modeBtn: { padding: '6px 18px', borderRadius: 6, border: '1px solid', cursor: 'pointer', fontFamily: 'Orbitron', fontSize: 9, letterSpacing: 1 },
  pomoBtn: { padding: '10px 32px', borderRadius: 8, border: '1px solid rgba(0,255,200,0.3)', background: 'rgba(0,255,200,0.1)', color: 'var(--cyan)', fontFamily: 'Orbitron', fontSize: 11, letterSpacing: 3, cursor: 'pointer' },
  cardFace: { position: 'absolute', inset: 0, borderRadius: 12, padding: 24, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' },
  cardNav: { padding: '8px 20px', borderRadius: 6, border: '1px solid rgba(0,255,200,0.2)', background: 'rgba(0,255,200,0.05)', color: 'var(--cyan)', fontFamily: 'Orbitron', fontSize: 9, letterSpacing: 2, cursor: 'pointer' },
  smallBtn: { padding: '6px 16px', borderRadius: 6, border: '1px solid rgba(0,255,200,0.3)', background: 'rgba(0,255,200,0.08)', color: 'var(--cyan)', fontFamily: 'Rajdhani', fontSize: 12, cursor: 'pointer' },
}
