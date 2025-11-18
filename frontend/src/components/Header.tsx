import React from 'react'
import { Clock, Wifi, WifiOff } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'
import apiClient from '../services/api'

const Header: React.FC = () => {
  const [currentTime, setCurrentTime] = React.useState<string>('')
  const [isConnected, setIsConnected] = React.useState<boolean>(true)
  const [apiError, setApiError] = React.useState<string | null>(null)
  const [trackTemp, setTrackTemp] = React.useState<number | null>(null)
  const [raceStatus, setRaceStatus] = React.useState<string>('LIVE')

  // Connect to WebSocket for real-time updates
  const { isConnected: wsConnected } = useWebSocket({
    url: 'ws://localhost:8000/ws/live-updates',
    onMessage: (message) => {
      if (message.type === 'RACE_STATE_UPDATE' && message.data) {
        setTrackTemp(message.data.track_temp)
      }
    },
    onConnect: () => {
      setIsConnected(true)
      setApiError(null)
    },
    onDisconnect: () => {
      setIsConnected(false)
    },
    onError: () => {
      setApiError('WebSocket connection failed')
    },
  })

  // Update time every second
  React.useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setCurrentTime(now.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }))
    }

    updateTime()
    const interval = setInterval(updateTime, 1000)

    return () => clearInterval(interval)
  }, [])

  // Check API health and get race data
  React.useEffect(() => {
    const checkAPIHealth = async () => {
      try {
        const health = await apiClient.getHealth()
        setIsConnected(health.status === 'healthy' || health.status === 'degraded')
        setApiError(null)

        // Try to get race status
        const raceStatus = await apiClient.getRaceStatus()
        setRaceStatus('RUNNING')
        setTrackTemp(raceStatus.leader ? 0 : null)
      } catch (error) {
        const message = error instanceof Error ? error.message : 'API unavailable'
        setApiError(message)
        setIsConnected(false)
      }
    }

    checkAPIHealth()
    const interval = setInterval(checkAPIHealth, 10000) // Check every 10 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <header className="bg-ferrari-black border-b-2 border-ferrari-red shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Ferrari Branding */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-ferrari-red rounded-lg flex items-center justify-center">
                <span className="text-ferrari-white font-bold text-xl">F</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-ferrari-white">
                  FERRARI F1
                </h1>
                <p className="text-ferrari-gray-400 text-sm">
                  Strategy Command Center
                </p>
              </div>
            </div>
          </div>

          {/* Race Status */}
          <div className="hidden md:flex items-center space-x-6">
            <div className="text-center">
              <p className="text-ferrari-gray-400 text-sm">RACE STATUS</p>
              <p className="text-ferrari-white font-bold">{raceStatus}</p>
            </div>
            <div className="text-center">
              <p className="text-ferrari-gray-400 text-sm">NEXT SESSION</p>
              <p className="text-ferrari-white font-bold">QUALI - 14:00</p>
            </div>
            <div className="text-center">
              <p className="text-ferrari-gray-400 text-sm">TRACK TEMP</p>
              <p className="text-ferrari-white font-bold">{trackTemp ? `${trackTemp}°C` : '--°C'}</p>
            </div>
          </div>

          {/* System Status */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-ferrari-gray-400" />
              <span className="text-ferrari-white font-mono text-lg">
                {currentTime}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <Wifi className="w-5 h-5 text-ferrari-gold" />
              ) : (
                <WifiOff className="w-5 h-5 text-ferrari-red" />
              )}
              <span className={`text-sm font-bold ${
                isConnected ? 'text-ferrari-gold' : 'text-ferrari-red'
              }`}>
                {isConnected ? 'LIVE' : 'OFFLINE'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 