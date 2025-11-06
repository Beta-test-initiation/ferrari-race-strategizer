import React from 'react'
import { AlertTriangle, Clock, Zap, TrendingUp } from 'lucide-react'

interface Alert {
  id: string
  type: 'critical' | 'warning' | 'info'
  message: string
  timestamp: Date
  driver?: 'HAM' | 'LEC'
  icon?: React.ReactNode
}

const LiveAlerts: React.FC = () => {
  const [alerts, setAlerts] = React.useState<Alert[]>([
    {
      id: '1',
      type: 'critical',
      message: 'PIT WINDOW OPEN - Hamilton optimal pit in 2 laps',
      timestamp: new Date(),
      driver: 'HAM',
      icon: <Clock className="w-5 h-5" />
    },
    {
      id: '2',
      type: 'warning',
      message: 'Track temperature rising - tire degradation increasing',
      timestamp: new Date(Date.now() - 30000),
      icon: <TrendingUp className="w-5 h-5" />
    },
    {
      id: '3',
      type: 'info',
      message: 'DRS enabled - undercut opportunity available',
      timestamp: new Date(Date.now() - 60000),
      icon: <Zap className="w-5 h-5" />
    }
  ])

  // TODO: Implement real-time alert system from backend
  React.useEffect(() => {
    const interval = setInterval(() => {
      // Simulate new alerts
      const newAlert: Alert = {
        id: Date.now().toString(),
        type: Math.random() > 0.7 ? 'critical' : Math.random() > 0.5 ? 'warning' : 'info',
        message: 'System update - Strategy recommendations refreshed',
        timestamp: new Date(),
        icon: <AlertTriangle className="w-5 h-5" />
      }
      
      setAlerts(prev => [newAlert, ...prev.slice(0, 4)]) // Keep only 5 latest alerts
    }, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

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
                  {alert.icon}
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