import React from 'react'
import { Timer, Flag, TrendingUp, Users, Thermometer } from 'lucide-react'

interface DriverData {
  name: string
  code: 'HAM' | 'LEC'
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
  const [raceData, setRaceData] = React.useState({
    currentLap: 32,
    totalLaps: 58,
    raceTime: '1:24:37',
    trackTemp: 42,
    airTemp: 28,
    weather: 'Clear',
    safetyCarDeployed: false
  })

  const [drivers, setDrivers] = React.useState<DriverData[]>([
    {
      name: 'Lewis Hamilton',
      code: 'HAM',
      position: 3,
      currentTire: 'MEDIUM',
      tireLaps: 14,
      lastLapTime: '1:28.452',
      gap: '+8.234',
      pitStops: 1,
      nextPitWindow: 'LAP 38-42',
      strategy: 'M-H-M'
    },
    {
      name: 'Charles Leclerc',
      code: 'LEC',
      position: 5,
      currentTire: 'HARD',
      tireLaps: 18,
      lastLapTime: '1:28.891',
      gap: '+15.678',
      pitStops: 1,
      nextPitWindow: 'LAP 45-50',
      strategy: 'M-H-M'
    }
  ])

  // TODO: Implement real-time data updates from backend
  React.useEffect(() => {
    const interval = setInterval(() => {
      setRaceData(prev => ({
        ...prev,
        currentLap: prev.currentLap + 1,
        trackTemp: prev.trackTemp + (Math.random() - 0.5) * 2
      }))
      
      setDrivers(prev => prev.map(driver => ({
        ...driver,
        tireLaps: driver.tireLaps + 1,
        lastLapTime: `1:${28 + Math.floor(Math.random() * 2)}.${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`
      })))
    }, 10000) // Update every 10 seconds

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
              {raceData.currentLap}/{raceData.totalLaps}
            </p>
          </div>
          <div className="text-center">
            <p className="text-ferrari-gray-400 text-sm">RACE TIME</p>
            <p className="text-ferrari-white font-bold text-xl font-mono">
              {raceData.raceTime}
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
            {raceData.trackTemp.toFixed(1)}°C
          </p>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Thermometer className="w-5 h-5 text-ferrari-silver" />
            <span className="text-ferrari-gray-400 text-sm">AIR TEMP</span>
          </div>
          <p className="text-2xl font-bold text-ferrari-white">
            {raceData.airTemp}°C
          </p>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-5 h-5 text-ferrari-gold" />
            <span className="text-ferrari-gray-400 text-sm">WEATHER</span>
          </div>
          <p className="text-2xl font-bold text-ferrari-white">
            {raceData.weather}
          </p>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-ferrari-red" />
            <span className="text-ferrari-gray-400 text-sm">SAFETY CAR</span>
          </div>
          <p className={`text-2xl font-bold ${
            raceData.safetyCarDeployed ? 'text-ferrari-yellow' : 'text-ferrari-silver'
          }`}>
            {raceData.safetyCarDeployed ? 'DEPLOYED' : 'CLEAR'}
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