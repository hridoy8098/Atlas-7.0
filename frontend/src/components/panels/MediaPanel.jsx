import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Music, Video, Image, Download, Play, Pause, SkipBack, SkipForward } from 'lucide-react'

const playlist = [
  { title: 'Blinding Lights', artist: 'The Weeknd', duration: '3:20', cover: '🎵' },
  { title: 'Starboy', artist: 'The Weeknd', duration: '3:50', cover: '🎵' },
  { title: 'Heat Waves', artist: 'Glass Animals', duration: '3:58', cover: '🎵' },
  { title: 'Believer', artist: 'Imagine Dragons', duration: '3:24', cover: '🎵' },
  { title: 'Shape of You', artist: 'Ed Sheeran', duration: '3:54', cover: '🎵' },
]

export default function MediaPanel() {
  const [activeTab, setActiveTab] = useState('music')
  const [currentTrack, setCurrentTrack] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const progressRef = useRef(null)

  const togglePlay = () => {
    if (!playing) {
      setPlaying(true)
      const interval = setInterval(() => {
        setProgress(p => {
          if (p >= 100) {
            clearInterval(interval)
            setPlaying(false)
            return 0
          }
          return p + 1
        })
      }, 300)
      progressRef.current = interval
    } else {
      clearInterval(progressRef.current)
      setPlaying(false)
    }
  }

  const nextTrack = () => {
    clearInterval(progressRef.current)
    setPlaying(false)
    setProgress(0)
    setCurrentTrack(t => (t + 1) % playlist.length)
  }

  const prevTrack = () => {
    clearInterval(progressRef.current)
    setPlaying(false)
    setProgress(0)
    setCurrentTrack(t => (t - 1 + playlist.length) % playlist.length)
  }

  const tabs = [
    { id: 'music', label: 'MUSIC', icon: Music },
    { id: 'video', label: 'VIDEO', icon: Video },
    { id: 'images', label: 'IMAGES', icon: Image },
    { id: 'downloads', label: 'DOWNLOAD', icon: Download },
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
        {activeTab === 'music' && (
          <motion.div key="music" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', gap: 10, height: '100%' }}>
            {/* Now Playing */}
            <div style={S.card}>
              <div style={{ textAlign: 'center', marginBottom: 12 }}>
                <div style={{ fontSize: 36, marginBottom: 8 }}>{playlist[currentTrack].cover}</div>
                <div style={{ fontFamily: 'Orbitron', fontSize: 13, color: 'var(--cyan)', letterSpacing: 1 }}>{playlist[currentTrack].title}</div>
                <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 2 }}>{playlist[currentTrack].artist}</div>
              </div>

              {/* Progress */}
              <div style={{ height: 3, background: 'rgba(0,255,200,0.1)', borderRadius: 2, marginBottom: 8, overflow: 'hidden' }}>
                <motion.div animate={{ width: `${progress}%` }} style={{ height: '100%', background: '#00ffc8', borderRadius: 2 }} />
              </div>

              {/* Controls */}
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16 }}>
                <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={prevTrack}
                  style={S.ctrlBtn}><SkipBack size={16} /></motion.button>
                <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={togglePlay}
                  style={{ ...S.playBtn, background: playing ? 'rgba(255,100,0,0.15)' : 'rgba(0,255,200,0.15)', borderColor: playing ? '#ff6600' : 'var(--cyan)' }}>
                  {playing ? <Pause size={20} /> : <Play size={20} />}
                </motion.button>
                <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={nextTrack}
                  style={S.ctrlBtn}><SkipForward size={16} /></motion.button>
              </div>
            </div>

            {/* Playlist */}
            <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 4 }}>
              {playlist.map((track, i) => (
                <motion.div key={i} whileHover={{ x: 3 }}
                  onClick={() => { setCurrentTrack(i); setPlaying(false); setProgress(0); clearInterval(progressRef.current) }}
                  style={{
                    ...S.trackItem,
                    background: currentTrack === i ? 'rgba(0,255,200,0.08)' : 'transparent',
                    borderLeft: currentTrack === i ? '2px solid #00ffc8' : '2px solid transparent',
                  }}>
                  <span style={{ fontSize: 16 }}>{track.cover}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, color: 'var(--cyan)' }}>{track.title}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>{track.artist}</div>
                  </div>
                  <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>{track.duration}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'video' && (
          <motion.div key="video" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', gap: 10, height: '100%' }}>
            <div style={S.card}>
              <div style={{ fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-dim)', letterSpacing: 2, marginBottom: 12 }}>YOUTUBE DOWNLOADER</div>
              <div style={{ display: 'flex', gap: 8 }}>
                <input value={youtubeUrl} onChange={e => setYoutubeUrl(e.target.value)}
                  placeholder="Paste YouTube URL..."
                  style={S.input} />
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  disabled={!youtubeUrl}
                  style={{ ...S.smallBtn, opacity: youtubeUrl ? 1 : 0.4 }}>FETCH</motion.button>
              </div>
            </div>
            <div style={{ ...S.card, flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ textAlign: 'center', color: 'var(--text-dim)' }}>
                <Video size={32} style={{ margin: '0 auto 8px', opacity: 0.3 }} />
                <div style={{ fontSize: 12 }}>Video player coming soon</div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'images' && (
          <motion.div key="images" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, height: '100%' }}>
            {[
              { label: 'Generate', desc: 'AI Image Generation', icon: '🎨', color: '#00ffc8' },
              { label: 'Remove BG', desc: 'Background Remover', icon: '✂️', color: '#00aaff' },
              { label: 'Meme', desc: 'Meme Generator', icon: '😂', color: '#ffaa00' },
              { label: 'Subtitles', desc: 'Auto Subtitle Gen', icon: '📝', color: '#ff88ff' },
              { label: 'Podcast', desc: 'AI Podcast Creator', icon: '🎙️', color: '#ff6600' },
              { label: 'Gallery', desc: 'Media Gallery', icon: '🖼️', color: '#00ff88' },
            ].map((img, i) => (
              <div key={i} style={S.card}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>{img.icon}</div>
                <div style={{ fontFamily: 'Orbitron', fontSize: 9, color: img.color, letterSpacing: 1, marginBottom: 4 }}>{img.label}</div>
                <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>{img.desc}</div>
              </div>
            ))}
          </motion.div>
        )}

        {activeTab === 'downloads' && (
          <motion.div key="downloads" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{ display: 'flex', flexDirection: 'column', gap: 8, height: '100%' }}>
            {[
              { file: 'video_2024.mp4', size: '145 MB', progress: 100 },
              { file: 'music_playlist.zip', size: '82 MB', progress: 100 },
              { file: 'project_backup.tar', size: '256 MB', progress: 64 },
              { file: 'ai_model_weights.bin', size: '512 MB', progress: 23 },
            ].map((dl, i) => (
              <div key={i} style={S.card}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ fontFamily: 'Share Tech Mono', fontSize: 12, color: 'var(--cyan)' }}>{dl.file}</span>
                  <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>{dl.size}</span>
                </div>
                <div style={{ height: 3, background: 'rgba(0,255,200,0.1)', borderRadius: 2, overflow: 'hidden' }}>
                  <motion.div initial={{ width: 0 }} animate={{ width: `${dl.progress}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    style={{ height: '100%', background: dl.progress === 100 ? '#00ff88' : '#00aaff', borderRadius: 2 }} />
                </div>
                <div style={{ fontSize: 9, color: 'var(--text-dim)', marginTop: 4, textAlign: 'right' }}>
                  {dl.progress === 100 ? 'COMPLETE' : `${dl.progress}%`}
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
  ctrlBtn: { width: 36, height: 36, borderRadius: '50%', border: '1px solid rgba(0,255,200,0.2)', background: 'rgba(0,255,200,0.05)', color: 'var(--cyan)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  playBtn: { width: 52, height: 52, borderRadius: '50%', border: '2px solid', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--cyan)' },
  trackItem: { display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', borderRadius: 6, cursor: 'pointer' },
  input: { flex: 1, background: 'rgba(0,255,200,0.04)', border: '1px solid rgba(0,255,200,0.2)', borderRadius: 6, padding: '8px 12px', color: 'var(--cyan)', fontSize: 12, outline: 'none', fontFamily: 'Rajdhani' },
  smallBtn: { padding: '8px 16px', borderRadius: 6, border: '1px solid rgba(0,255,200,0.3)', background: 'rgba(0,255,200,0.08)', color: 'var(--cyan)', fontFamily: 'Rajdhani', fontSize: 12, cursor: 'pointer' },
}
