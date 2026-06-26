// MainPage.jsx — Atlas 7.0 Iron Man HUD Layout
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import useAtlasStore from '../store/useAtlasStore'
import { getMetrics, getWeather, getPrayerTimes, getUserConfig } from '../services/api'
import IronManHUD from '../components/hud/IronManHUD'

export default function MainPage() {
  const { setMetrics, setWeather, setPrayerTimes, setUserName } = useAtlasStore()
  const location = useLocation()
  const panel = location.pathname.replace('/', '') || 'chat'

  useEffect(() => {
    const poll = async () => { try { setMetrics(await getMetrics()) } catch {} }
    poll()
    const iv = setInterval(poll, 3000)
    return () => clearInterval(iv)
  }, [])

  useEffect(() => {
    getWeather().then(setWeather).catch(() => {})
    getPrayerTimes().then(setPrayerTimes).catch(() => {})
    getUserConfig().then(cfg => { if (cfg.user_name) setUserName(cfg.user_name) }).catch(() => {})
  }, [])

  return <IronManHUD panel={panel} />
}