import React from 'react'
import { Flag, TrendingUp, Users, Thermometer } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'
import apiClient from '../services/api'
import type { RaceState } from '../services/api'

interface DriverData {
  name: string
  code: string
  position: number
  currentTire: 'SOFT' | 'MEDIUM' | 'HARD'
  tireLaps: number
  lastLapTime: string
  gap: string
  pitStops: number
  nextPitWindow: string
  strategy: string
}

const StrategyOverview: React.FC = () => {
  const [raceData, setRaceData] = React.useState<Omit<RaceState, 'drivers'> | null>(null)
  const [drivers, setDrivers] = React.useState<DriverData[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  // Connect to WebSocket for real-time updates
  useWebSocket({
    url: 'ws://localhost:8000/ws/live-updates',
    onMessage: (message) => {
      if (message.type === 'RACE_STATE_UPDATE' && message.data) {
        // Update with WebSocket data
        const data = message.data
        setRaceData(prev => prev ? {
          ...prev,
          current_lap: data.current_lap ?? prev.current_lap,
          track_temp: data.track_temp ?? prev.track_temp,
          air_temp: data.air_temp ?? prev.air_temp,
        } : null)
      }
    },
  })

  // Load initial race data
  React.useEffect(() => {
    const loadRaceData = async () => {
      try {
        setLoading(true)
        const race = await apiClient.getCurrentRaceState()
        setRaceData(race)

        // Convert API drivers to our format
        const formattedDrivers: DriverData[] = race.drivers.slice(0, 2).map(driver => ({
          name: driver.name,
          code: driver.name === 'Hamilton' ? 'HAM' : driver.name === 'Leclerc' ? 'LEC' : 'N/A',
          position: driver.position,
          currentTire: driver.tire_compound as 'SOFT' | 'MEDIUM' | 'HARD',
          tireLaps: driver.tire_age,
          lastLapTime: driver.lap_time,
          gap: `+${driver.gap.toFixed(3)}`,
          pitStops: driver.pit_stops,
          nextPitWindow: 'LAP 38-42',
          strategy: 'M-H-M'
        }))

        setDrivers(formattedDrivers)
        setError(null)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load race data'
        setError(message)
        // Use fallback data if API is unavailable
        setRaceData({
          race_name: 'Abu Dhabi GP',
          season: 2025,
          current_lap: 32,
          total_laps: 58,
          race_time: '1:24:37',
          track_temp: 42,
          air_temp: 28,
          weather: 'Clear',
          safety_car_active: false,
          status: 'RUNNING',
          timestamp: new Date().toISOString(),
        })
      } finally {
        setLoading(false)
      }
    }

    loadRaceData()
    const interval = setInterval(loadRaceData, 10000) // Refresh every 10 seconds

    return () => clearInterval(interval)
  }, [])

  const getTireColor = (tire: string) => {
    switch (tire) {
      case 'SOFT':
        return 'bg-ferrari-red text-ferrari-white'
      case 'MEDIUM':
        return 'bg-ferrari-yellow text-ferrari-black'
      case 'HARD':
        return 'bg-ferrari-white text-ferrari-black'
      default:
        return 'bg-ferrari-gray-500 text-ferrari-white'
    }
  }

  const getPositionColor = (position: number) => {
    if (position <= 3) return 'text-ferrari-gold'
    if (position <= 10) return 'text-ferrari-silver'
    return 'text-ferrari-gray-400'
  }

  return (
    <div className="dashboard-panel p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-ferrari-white flex items-center">
          <Flag className="w-7 h-7 mr-3 text-ferrari-red" />
          RACE STRATEGY OVERVIEW
        </h2>
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <p className="text-ferrari-gray-400 text-sm">LAP</p>
            <p className="text-ferrari-white font-bold text-xl">
              {raceData ? `${raceData.current_lap}/${raceData.total_laps}` : '--/--'}
            </p>
          </div>
          <div className="text-center">
            <p className="text-ferrari-gray-400 text-sm">RACE TIME</p>
            <p className="text-ferrari-white font-bold text-xl font-mono">
              {raceData ? raceData.race_time : '--:--:--'}
            </p>
          </div>
        </div>
      </div>

      {/* Track Conditions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Thermometer className="w-5 h-5 text-ferrari-yellow" />
            <span className="text-ferrari-gray-400 text-sm">TRACK TEMP</span>
          </div>
          <p className="text-2xl font-bold text-ferrari-white">
            {raceData ? raceData.track_temp.toFixed(1) : '--'}°C
          </p>
        </div>

        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Thermometer className="w-5 h-5 text-ferrari-silver" />
            <span className="text-ferrari-gray-400 text-sm">AIR TEMP</span>
          </div>
          <p className="text-2xl font-bold text-ferrari-white">
            {raceData ? raceData.air_temp : '--'}°C
          </p>
        </div>

        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-5 h-5 text-ferrari-gold" />
            <span className="text-ferrari-gray-400 text-sm">WEATHER</span>
          </div>
          <p className="text-2xl font-bold text-ferrari-white">
            {raceData ? raceData.weather : '--'}
          </p>
        </div>

        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-ferrari-red" />
            <span className="text-ferrari-gray-400 text-sm">SAFETY CAR</span>
          </div>
          <p className={`text-2xl font-bold ${
            raceData && raceData.safety_car_active ? 'text-ferrari-yellow' : 'text-ferrari-silver'
          }`}>
            {raceData && raceData.safety_car_active ? 'DEPLOYED' : 'CLEAR'}
          </p>
        </div>
      </div>

      {/* Driver Status */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-ferrari-white mb-4">DRIVER STATUS</h3>
        {drivers.map((driver) => (
          <div key={driver.code} className="bg-ferrari-gray-900 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-8 gap-4 items-center">
              <div className="md:col-span-2">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    driver.code === 'HAM' ? 'bg-ferrari-gold text-ferrari-black' : 'bg-ferrari-red text-ferrari-white'
                  }`}>
                    {driver.code}
                  </div>
                  <div>
                    <p className="text-ferrari-white font-bold">{driver.name}</p>
                    <p className={`text-lg font-bold ${getPositionColor(driver.position)}`}>
                      P{driver.position}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">TIRE</p>
                <div className="flex items-center justify-center space-x-2">
                  <span className={`px-2 py-1 rounded font-bold text-sm ${getTireColor(driver.currentTire)}`}>
                    {driver.currentTire}
                  </span>
                  <span className="text-ferrari-white font-mono">
                    {driver.tireLaps} laps
                  </span>
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">LAST LAP</p>
                <p className="text-ferrari-white font-mono text-lg">
                  {driver.lastLapTime}
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">GAP</p>
                <p className="text-ferrari-white font-mono text-lg">
                  {driver.gap}
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">PIT STOPS</p>
                <p className="text-ferrari-white font-bold text-lg">
                  {driver.pitStops}
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">NEXT PIT</p>
                <p className="text-ferrari-yellow font-bold">
                  {driver.nextPitWindow}
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">STRATEGY</p>
                <p className="text-ferrari-white font-bold">
                  {driver.strategy}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default StrategyOverview 