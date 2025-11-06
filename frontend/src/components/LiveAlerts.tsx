import React from 'react'
import { AlertTriangle } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'

interface Alert {
  id: string
  type: 'critical' | 'warning' | 'info'
  message: string
  timestamp: Date
  driver?: 'HAM' | 'LEC'
}

const LiveAlerts: React.FC = () => {
  const [alerts, setAlerts] = React.useState<Alert[]>([])
  const apiUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

  // Connect to WebSocket for real-time alerts
  useWebSocket({
    url: `${apiUrl}/ws/alerts`,
    onMessage: (message) => {
      if (message.type === 'alert') {
        const newAlert: Alert = {
          id: message.data?.id || Date.now().toString(),
          type: (message.data?.severity || 'info').toLowerCase() as 'critical' | 'warning' | 'info',
          message: message.data?.message || 'Alert received',
          timestamp: new Date(message.data?.timestamp || new Date()),
          driver: message.data?.driver
        }

        setAlerts(prev => [newAlert, ...prev.slice(0, 4)]) // Keep only 5 latest alerts
      }
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
    }
  })

  const getAlertClasses = (type: Alert['type']) => {
    switch (type) {
      case 'critical':
        return 'alert-critical border-ferrari-red'
      case 'warning':
        return 'alert-warning border-ferrari-yellow'
      case 'info':
        return 'alert-info border-ferrari-gray-500'
      default:
        return 'alert-info border-ferrari-gray-500'
    }
  }

  const getDriverColor = (driver?: string) => {
    switch (driver) {
      case 'HAM':
        return 'text-ferrari-gold'
      case 'LEC':
        return 'text-ferrari-red'
      default:
        return 'text-ferrari-gray-400'
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="dashboard-panel p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-ferrari-white flex items-center">
          <AlertTriangle className="w-6 h-6 mr-2 text-ferrari-red" />
          LIVE ALERTS
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-ferrari-red rounded-full animate-flash"></div>
          <span className="text-ferrari-gray-400 text-sm">ACTIVE</span>
        </div>
      </div>

      <div className="space-y-2">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`p-3 rounded-lg border-l-4 ${getAlertClasses(alert.type)} transition-all duration-300 hover:shadow-lg`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <div className="mt-1">
                  <AlertTriangle className="w-5 h-5 text-ferrari-red" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    {alert.driver && (
                      <span className={`font-bold text-sm ${getDriverColor(alert.driver)}`}>
                        {alert.driver}
                      </span>
                    )}
                    <span className="text-ferrari-gray-400 text-xs font-mono">
                      {formatTime(alert.timestamp)}
                    </span>
                  </div>
                  <p className="text-sm font-medium">
                    {alert.message}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {alerts.length === 0 && (
        <div className="text-center py-8">
          <p className="text-ferrari-gray-400">No active alerts</p>
        </div>
      )}
    </div>
  )
}

export default LiveAlerts 