// HUDCenter.jsx — Robot + Chat
import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import useAtlasStore from '../../store/useAtlasStore'
import { sendCommand } from '../../services/api'

// ── CSS animations injected once ──
const ANIM_CSS = `
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=css');
@keyframes hudFloat { 0%,100%{transform:translateY(0) rotateY(0deg)} 50%{transform:translateY(-8px) rotateY(3deg)} }
@keyframes hudEye { 0%,100%{opacity:1;box-shadow:0 0 8px var(--ec,#00ffc8)} 50%{opacity:0.5;box-shadow:0 0 3px var(--ec,#00ffc8)} }
@keyframes hudReactor { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
@keyframes hudReactor2 { from{transform:rotate(0deg)} to{transform:rotate(-360deg)} }
@keyframes hudScan { 0%{top:0%} 100%{top:100%} }
@keyframes hudRing { 0%{transform:translate(-50%,-50%) scale(1);opacity:0.5} 100%{transform:translate(-50%,-50%) scale(2.6);opacity:0} }
@keyframes hudDot { 0%,100%{transform:translateY(0);opacity:0.4} 50%{transform:translateY(-5px);opacity:1} }
@keyframes hudSpeakBar { 0%,100%{height:4px} 50%{height:16px} }
@keyframes hudAntenna { 0%,100%{box-shadow:0 0 6px #00ffc8,0 0 12px #00ffc8} 50%{box-shadow:0 0 14px #00ffc8,0 0 28px rgba(0,255,200,0.5)} }
`

function StyleOnce() {
  if (typeof document !== 'undefined' && !document.getElementById('atlas-hud-anim')) {
    const s = document.createElement('style')
    s.id = 'atlas-hud-anim'
    s.textContent = ANIM_CSS
    document.head.appendChild(s)
  }
  return null
}

// ── Color map per state ──
const STATE_COLORS = {
  idle:      { main:'#00ffc8', glow:'rgba(0,255,200,0.35)', ring:'rgba(0,255,200,0.3)' },
  listening: { main:'#ff7700', glow:'rgba(255,119,0,0.5)',  ring:'rgba(255,119,0,0.4)' },
  thinking:  { main:'#9933ff', glow:'rgba(153,51,255,0.5)', ring:'rgba(153,51,255,0.4)' },
  speaking:  { main:'#00aaff', glow:'rgba(0,170,255,0.5)',  ring:'rgba(0,170,255,0.4)' },
}

// ── 3D CSS Robot ──
function AtlasRobot({ state, onClick }) {
  const c = STATE_COLORS[state] || STATE_COLORS.idle
  const isIdle = state === 'idle'

  return (
    <div onClick={onClick} style={{ position:'relative', display:'flex', flexDirection:'column', alignItems:'center', cursor:'pointer', userSelect:'none' }}>
      <StyleOnce />

      {/* Pulse rings */}
      {[0,1,2].map(i => (
        <div key={i} style={{ position:'absolute', width:150, height:150, borderRadius:'50%', border:`1px solid ${c.ring}`, animation:`hudRing 2.2s ease-out ${i*0.7}s infinite`, top:'50%', left:'50%', pointerEvents:'none' }} />
      ))}

      {/* Robot */}
      <div style={{ display:'flex', flexDirection:'column', alignItems:'center', filter:`drop-shadow(0 0 18px ${c.glow})`, animation: isIdle ? 'hudFloat 4s ease-in-out infinite' : 'none' }}>

        {/* Antenna */}
        <div style={{ width:2, height:20, background:'rgba(0,255,200,0.25)', margin:'0 auto' }} />
        <div style={{ width:10, height:10, borderRadius:'50%', background:c.main, boxShadow:`0 0 10px ${c.main}`, margin:'-4px auto 0', animation:'hudAntenna 1.5s ease-in-out infinite' }} />

        {/* Head */}
        <div style={{ width:80, height:62, background:'linear-gradient(150deg,#001812,#002e22)', border:`1.5px solid ${c.main}44`, borderRadius:'12px 12px 8px 8px', marginTop:4, position:'relative', overflow:'hidden', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
          <div style={{ position:'absolute', top:0, left:0, right:0, height:1, background:`linear-gradient(90deg,transparent,${c.main},transparent)` }} />
          <div style={{ position:'absolute', left:0, right:0, height:1, background:`rgba(0,255,200,0.3)`, animation:'hudScan 2.5s linear infinite' }} />

          {/* Eyes */}
          <div style={{ display:'flex', gap:16 }}>
            {[0,0.25].map((d,i) => (
              <div key={i} style={{ width:12, height:12, borderRadius:'50%', background:c.main, '--ec':c.main, animation:`hudEye ${state==='listening'?'0.5s':'2.2s'} ease-in-out ${d}s infinite` }} />
            ))}
          </div>

          {/* Mouth */}
          <div style={{ display:'flex', alignItems:'flex-end', gap:3, height:20, justifyContent:'center' }}>
            {state === 'speaking'
              ? [0,0.08,0.16,0.08,0].map((d,i) => (
                  <div key={i} style={{ width:3, background:c.main, borderRadius:2, animation:`hudSpeakBar 0.45s ease-in-out ${d}s infinite` }} />
                ))
              : <div style={{ width:26, height:2, background:c.main+'66', borderRadius:1 }} />
            }
          </div>
        </div>

        {/* Neck */}
        <div style={{ width:14, height:7, background:'rgba(0,20,14,0.9)', borderLeft:`1px solid ${c.main}33`, borderRight:`1px solid ${c.main}33` }} />

        {/* Body + Arms */}
        <div style={{ position:'relative', display:'flex', alignItems:'flex-start', justifyContent:'center' }}>
          {/* Arms */}
          {[-1,1].map(side => (
            <div key={side} style={{ position:'absolute', top:6, [side===-1?'left':'right']:-16, width:13, height:68, background:'rgba(0,18,12,0.9)', border:`1px solid ${c.main}28`, borderRadius:7, display:'flex', alignItems:'flex-end', justifyContent:'center', paddingBottom:4 }}>
              <div style={{ width:8, height:8, borderRadius:'50%', background:c.main, boxShadow:`0 0 5px ${c.main}` }} />
            </div>
          ))}

          {/* Body */}
          <div style={{ width:100, height:100, background:'linear-gradient(150deg,#001812,#002e22)', border:`1.5px solid ${c.main}44`, borderRadius:14, position:'relative', overflow:'hidden', display:'flex', alignItems:'center', justifyContent:'center' }}>
            <div style={{ position:'absolute', left:0, right:0, height:1, background:`rgba(0,255,200,0.25)`, animation:'hudScan 3s linear infinite 1s' }} />
            {[-1,1].map(s => (
              <div key={s} style={{ position:'absolute', top:16, [s===-1?'left':'right']:8, width:5, height:5, borderRadius:'50%', background:c.main, boxShadow:`0 0 6px ${c.main}` }} />
            ))}

            {/* Arc Reactor */}
            <div style={{ position:'relative', width:42, height:42, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <div style={{ position:'absolute', inset:0, borderRadius:'50%', border:`2px solid ${c.main}`, borderTopColor:'transparent', animation:'hudReactor 2s linear infinite' }} />
              <div style={{ position:'absolute', inset:6, borderRadius:'50%', border:`1.5px solid ${c.main}55`, borderBottomColor:'transparent', animation:'hudReactor2 1.5s linear infinite' }} />
              <div style={{ width:16, height:16, borderRadius:'50%', background:`radial-gradient(circle,#fff 0%,${c.main} 45%,transparent 80%)`, boxShadow:`0 0 12px ${c.main},0 0 24px ${c.main}66` }} />
            </div>

            {/* Chest lines */}
            <div style={{ position:'absolute', bottom:10, left:10, right:10, display:'flex', flexDirection:'column', gap:3 }}>
              {[1,0.6,0.3].map((o,i) => <div key={i} style={{ height:1, background:c.main, opacity:o, borderRadius:1 }} />)}
            </div>
          </div>
        </div>

        {/* Legs */}
        <div style={{ display:'flex', gap:10, marginTop:4 }}>
          {[0,1].map(i => (
            <div key={i} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:2 }}>
              <div style={{ width:18, height:34, background:'rgba(0,18,12,0.9)', border:`1px solid ${c.main}28`, borderRadius:6 }} />
              <div style={{ width:24, height:8, background:'rgba(0,18,12,0.9)', border:`1px solid ${c.main}33`, borderRadius:4 }} />
            </div>
          ))}
        </div>
      </div>

      {/* State label */}
      <div style={{ marginTop:10, fontFamily:'Orbitron,monospace', fontSize:8, letterSpacing:2, color:c.main, opacity:0.8 }}>
        {state==='idle' && '● STANDBY'}
        {state==='listening' && '◉ LISTENING...'}
        {state==='thinking' && '◌ THINKING...'}
        {state==='speaking' && '▶ SPEAKING...'}
      </div>
      <div style={{ fontSize:9, color:'rgba(0,255,200,0.35)', marginTop:3 }}>
        {state === 'idle' ? 'CLICK TO SPEAK' : ''}
      </div>
    </div>
  )
}

// ── Voice hook ──
function useVoice(onResult) {
  const recogRef = useRef(null)
  const supported = typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)

  const start = useCallback(() => {
    if (!supported) return false
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const rec = new SR()
    rec.lang = 'bn-BD'
    rec.interimResults = false
    rec.maxAlternatives = 1
    rec.onresult = (e) => { onResult(e.results[0][0].transcript) }
    rec.onerror = () => { onResult(null) }
    rec.onend = () => {}
    rec.start()
    recogRef.current = rec
    return true
  }, [supported, onResult])

  const stop = useCallback(() => { recogRef.current?.stop() }, [])
  return { supported, start, stop }
}

// ── Panel imports ──
import SystemPanel from '../panels/SystemPanel'
import AnalyticsPanel from '../panels/AnalyticsPanel'
import SecurityPanel from '../panels/SecurityPanel'
import StudyPanel from '../panels/StudyPanel'
import BangladeshPanel from '../panels/BangladeshPanel'
import MediaPanel from '../panels/MediaPanel'
import MLPanel from '../panels/MLPanel'

const PANEL_COMPONENTS = {
  system: SystemPanel,
  analytics: AnalyticsPanel,
  security: SecurityPanel,
  study: StudyPanel,
  bangladesh: BangladeshPanel,
  media: MediaPanel,
  ml: MLPanel,
}

// ── Main ──
export default function HUDCenter({ panel = 'chat' }) {
  const { messages, addMessage, isProcessing, setProcessing, userName } = useAtlasStore()
  const [robotState, setRobotState] = useState('idle')
  const [isListening, setIsListening] = useState(false)
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior:'smooth' }) }, [messages])

  useEffect(() => {
    if (isListening) setRobotState('listening')
    else if (isProcessing) setRobotState('thinking')
    else setRobotState('idle')
  }, [isListening, isProcessing])

  const send = async (text) => {
    const t = (text || input).trim()
    if (!t || isProcessing) return
    setInput('')
    addMessage('user', t)
    setProcessing(true)
    try {
      const res = await sendCommand(t)
      if (res.response) {
        addMessage('assistant', res.response)
        setRobotState('speaking')
        setTimeout(() => { if (!isProcessing) setRobotState('idle') }, 2800)
      }
    } catch {
      addMessage('assistant', '❌ Server unreachable. Backend চলছে কিনা দেখো।')
    } finally {
      setProcessing(false)
    }
  }

  const { supported: voiceOk, start: startV, stop: stopV } = useVoice((transcript) => {
    setIsListening(false)
    if (transcript) send(transcript)
  })

  const handleRobotClick = () => {
    if (isProcessing) return
    if (isListening) { stopV(); setIsListening(false) }
    else {
      if (!voiceOk) { addMessage('assistant', '⚠️ Chrome browser এ voice কাজ করে।'); return }
      if (startV()) setIsListening(true)
    }
  }

  // Show full panel if not chat
  const PanelComp = panel !== 'chat' ? PANEL_COMPONENTS[panel] : null
  if (PanelComp) {
    return (
      <div style={{ display:'flex', flexDirection:'column', overflow:'auto', padding:4 }}>
        <PanelComp />
      </div>
    )
  }

  return (
    <div style={S.center}>
      {/* HUD decorative rings */}
      <div style={S.hudRing1} />
      <div style={S.hudRing2} />

      {/* Top: Robot */}
      <div style={S.robotArea}>
        <AtlasRobot state={robotState} onClick={handleRobotClick} />
      </div>

      {/* Bottom: Messages + Input */}
      <div style={S.chatArea}>
        <div style={S.messages}>
          {messages.length === 0 && (
            <div style={S.empty}>
              <span style={S.emptyIcon}>⬡</span>
              <span style={S.emptyText}>ATLAS READY — Robot এ click করো বা নিচে type করো</span>
            </div>
          )}
          <AnimatePresence>
            {messages.map(msg => (
              <motion.div key={msg.id} initial={{ opacity:0, y:8 }} animate={{ opacity:1, y:0 }} transition={{ duration:0.2 }}
                style={{
                  ...S.bubble,
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  background: msg.role === 'user' ? 'rgba(0,255,200,0.07)' : 'rgba(0,20,50,0.8)',
                  borderColor: msg.role === 'user' ? 'rgba(0,255,200,0.3)' : 'rgba(0,120,255,0.25)',
                }}>
                <div style={S.bubbleHeader}>
                  <span style={{ fontFamily:'Orbitron,monospace', fontSize:9, letterSpacing:1 }}>
                    {msg.role === 'user' ? '▸ ' + userName.toUpperCase() : '▸ ATLAS'}
                  </span>
                  <span style={{ fontSize:9, opacity:0.35 }}>{msg.time}</span>
                </div>
                <pre style={S.bubbleText}>{msg.text}</pre>
              </motion.div>
            ))}
          </AnimatePresence>

          {isProcessing && (
            <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }}
              style={{ ...S.bubble, alignSelf:'flex-start', borderColor:'rgba(153,51,255,0.3)', background:'rgba(20,0,40,0.8)' }}>
              <div style={{ display:'flex', gap:5, alignItems:'center' }}>
                <style>{`@keyframes dotB{0%,100%{transform:translateY(0);opacity:.4}50%{transform:translateY(-5px);opacity:1}}`}</style>
                {[0,1,2].map(i => <div key={i} style={{ width:6, height:6, borderRadius:'50%', background:'#9933ff', animation:`dotB 1s ease-in-out ${i*0.2}s infinite` }} />)}
                <span style={{ fontFamily:'Orbitron,monospace', fontSize:9, color:'#aa66ff', letterSpacing:2, marginLeft:4 }}>PROCESSING</span>
              </div>
            </motion.div>
          )}
          <div ref={bottomRef} />
        </div>

        <div style={S.inputRow}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
            placeholder="Command দাও... (Enter to send)"
            rows={2}
            style={S.input}
          />
          <motion.button whileHover={{ scale:1.05 }} whileTap={{ scale:0.95 }}
            onClick={() => send()}
            disabled={isProcessing || !input.trim()}
            style={{ ...S.sendBtn, opacity: isProcessing || !input.trim() ? 0.3 : 1 }}>▶</motion.button>
        </div>
      </div>
    </div>
  )
}

const S = {
  center: { display:'flex', flexDirection:'column', position:'relative', overflow:'hidden' },
  hudRing1: { position:'absolute', width:320, height:320, borderRadius:'50%', border:'1px solid rgba(0,255,200,0.06)', top:'30%', left:'50%', transform:'translate(-50%,-50%)', pointerEvents:'none' },
  hudRing2: { position:'absolute', width:240, height:240, borderRadius:'50%', border:'1px solid rgba(0,255,200,0.04)', top:'30%', left:'50%', transform:'translate(-50%,-50%)', pointerEvents:'none' },
  robotArea: { display:'flex', alignItems:'center', justifyContent:'center', paddingTop:12, flexShrink:0 },
  chatArea: { flex:1, display:'flex', flexDirection:'column', gap:6, overflow:'hidden', padding:'8px 6px 4px' },
  messages: { flex:1, overflowY:'auto', display:'flex', flexDirection:'column', gap:7, paddingRight:4 },
  empty: { display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:8, flex:1, opacity:0.4, paddingTop:20 },
  emptyIcon: { fontSize:30, color:'#00ffc8' },
  emptyText: { fontSize:10, color:'rgba(0,255,200,0.6)', fontFamily:'Orbitron,monospace', letterSpacing:2, textAlign:'center' },
  bubble: { maxWidth:'85%', padding:'8px 12px', borderRadius:8, border:'1px solid' },
  bubbleHeader: { display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:4, color:'rgba(0,255,200,0.45)' },
  bubbleText: { fontSize:12, color:'#d0eee0', lineHeight:1.65, whiteSpace:'pre-wrap', fontFamily:'Rajdhani,sans-serif', margin:0 },
  inputRow: { display:'flex', gap:6, flexShrink:0 },
  input: { flex:1, background:'rgba(0,255,200,0.04)', border:'1px solid rgba(0,255,200,0.2)', borderRadius:6, padding:'8px 12px', color:'#00ffc8', fontFamily:'Share Tech Mono,monospace', fontSize:12, resize:'none', outline:'none', lineHeight:1.5 },
  sendBtn: { width:44, background:'rgba(0,255,200,0.1)', border:'1px solid rgba(0,255,200,0.25)', borderRadius:6, color:'#00ffc8', fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 },
}