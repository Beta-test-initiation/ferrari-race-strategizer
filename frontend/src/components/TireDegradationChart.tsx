import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingDown, Info, AlertTriangle } from 'lucide-react'

interface TireData {
  lap: number
  hamilton_time: number
  leclerc_time: number
  hamilton_tire: string
  leclerc_tire: string
  track_temp: number
  predicted_hamilton: number
  predicted_leclerc: number
}

const TireDegradationChart: React.FC = () => {
  const [selectedDriver, setSelectedDriver] = React.useState<'both' | 'HAM' | 'LEC'>('both')
  const [selectedMetric, setSelectedMetric] = React.useState<'lap_time' | 'degradation'>('lap_time')
  
  const [tireData, setTireData] = React.useState<TireData[]>([
    { lap: 1, hamilton_time: 88.234, leclerc_time: 88.456, hamilton_tire: 'MEDIUM', leclerc_tire: 'MEDIUM', track_temp: 40, predicted_hamilton: 88.250, predicted_leclerc: 88.470 },
    { lap: 5, hamilton_time: 88.567, leclerc_time: 88.789, hamilton_tire: 'MEDIUM', leclerc_tire: 'MEDIUM', track_temp: 41, predicted_hamilton: 88.580, predicted_leclerc: 88.800 },
    { lap: 10, hamilton_time: 89.123, leclerc_time: 89.234, hamilton_tire: 'MEDIUM', leclerc_tire: 'MEDIUM', track_temp: 42, predicted_hamilton: 89.140, predicted_leclerc: 89.250 },
    { lap: 15, hamilton_time: 89.567, leclerc_time: 89.678, hamilton_tire: 'MEDIUM', leclerc_tire: 'MEDIUM', track_temp: 43, predicted_hamilton: 89.580, predicted_leclerc: 89.690 },
    { lap: 20, hamilton_time: 88.345, leclerc_time: 88.456, hamilton_tire: 'HARD', leclerc_tire: 'HARD', track_temp: 44, predicted_hamilton: 88.360, predicted_leclerc: 88.470 },
    { lap: 25, hamilton_time: 88.567, leclerc_time: 88.678, hamilton_tire: 'HARD', leclerc_tire: 'HARD', track_temp: 43, predicted_hamilton: 88.580, predicted_leclerc: 88.690 },
    { lap: 30, hamilton_time: 88.789, leclerc_time: 88.890, hamilton_tire: 'HARD', leclerc_tire: 'HARD', track_temp: 42, predicted_hamilton: 88.800, predicted_leclerc: 88.900 },
    { lap: 35, hamilton_time: 89.012, leclerc_time: 89.123, hamilton_tire: 'HARD', leclerc_tire: 'HARD', track_temp: 41, predicted_hamilton: 89.020, predicted_leclerc: 89.130 },
  ])

  // TODO: Implement real-time data updates from ML backend
  React.useEffect(() => {
    const interval = setInterval(() => {
      setTireData(prev => {
        const lastLap = prev[prev.length - 1]?.lap || 0
        const newLap = lastLap + 1
        
        const newData: TireData = {
          lap: newLap,
          hamilton_time: 88.5 + Math.random() * 1.5,
          leclerc_time: 88.7 + Math.random() * 1.5,
          hamilton_tire: newLap > 20 ? 'HARD' : 'MEDIUM',
          leclerc_tire: newLap > 20 ? 'HARD' : 'MEDIUM',
          track_temp: 40 + Math.random() * 5,
          predicted_hamilton: 88.6 + Math.random() * 1.2,
          predicted_leclerc: 88.8 + Math.random() * 1.2
        }
        
        return [...prev.slice(-20), newData] // Keep last 20 data points
      })
    }, 5000) // Update every 5 seconds

    return () => clearInterval(interval)
  }, [])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-ferrari-gray-900 border border-ferrari-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-ferrari-white font-bold mb-2">LAP {label}</p>
          <div className="space-y-1">
            {payload.map((entry: any, index: number) => (
              <p key={index} className="text-sm" style={{ color: entry.color }}>
                {entry.name}: {entry.value.toFixed(3)}s
              </p>
            ))}
          </div>
          <p className="text-ferrari-gray-400 text-xs mt-2">
            Track: {data.track_temp?.toFixed(1)}°C
          </p>
        </div>
      )
    }
    return null
  }

  const getLineColor = (driver: string, type: 'actual' | 'predicted') => {
    if (driver === 'hamilton') {
      return type === 'actual' ? '#FFD700' : '#FFD700'
    } else {
      return type === 'actual' ? '#DC143C' : '#DC143C'
    }
  }

  const handleDriverChange = (driver: 'both' | 'HAM' | 'LEC') => {
    setSelectedDriver(driver)
  }

  const handleMetricChange = (metric: 'lap_time' | 'degradation') => {
    setSelectedMetric(metric)
  }

  return (
    <div className="dashboard-panel p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-ferrari-white flex items-center">
          <TrendingDown className="w-6 h-6 mr-2 text-ferrari-red" />
          TIRE DEGRADATION ANALYSIS
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-ferrari-gold rounded-full animate-pulse"></div>
          <span className="text-ferrari-gray-400 text-sm">LIVE DATA</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex items-center space-x-2">
          <span className="text-ferrari-gray-400 text-sm">DRIVER:</span>
          <div className="flex space-x-1">
            {(['both', 'HAM', 'LEC'] as const).map((driver) => (
              <button
                key={driver}
                onClick={() => handleDriverChange(driver)}
                className={`px-3 py-1 rounded text-sm font-bold transition-colors ${
                  selectedDriver === driver
                    ? 'bg-ferrari-red text-ferrari-white'
                    : 'bg-ferrari-gray-700 text-ferrari-gray-300 hover:bg-ferrari-gray-600'
                }`}
              >
                {driver === 'both' ? 'BOTH' : driver}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-ferrari-gray-400 text-sm">METRIC:</span>
          <div className="flex space-x-1">
            {(['lap_time', 'degradation'] as const).map((metric) => (
              <button
                key={metric}
                onClick={() => handleMetricChange(metric)}
                className={`px-3 py-1 rounded text-sm font-bold transition-colors ${
                  selectedMetric === metric
                    ? 'bg-ferrari-red text-ferrari-white'
                    : 'bg-ferrari-gray-700 text-ferrari-gray-300 hover:bg-ferrari-gray-600'
                }`}
              >
                {metric === 'lap_time' ? 'LAP TIME' : 'DEGRADATION'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={tireData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="lap" 
              stroke="#9CA3AF" 
              tick={{ fill: '#9CA3AF' }}
              label={{ value: 'Lap', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
            />
            <YAxis 
              stroke="#9CA3AF" 
              tick={{ fill: '#9CA3AF' }}
              label={{ value: 'Lap Time (s)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              domain={['dataMin - 0.5', 'dataMax + 0.5']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ color: '#FFFFFF' }}
              iconType="line"
            />
            
            {(selectedDriver === 'both' || selectedDriver === 'HAM') && (
              <>
                <Line 
                  type="monotone" 
                  dataKey="hamilton_time" 
                  stroke="#FFD700" 
                  strokeWidth={3}
                  dot={{ fill: '#FFD700', strokeWidth: 2, r: 4 }}
                  name="Hamilton (Actual)"
                  connectNulls={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="predicted_hamilton" 
                  stroke="#FFD700" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Hamilton (Predicted)"
                  connectNulls={false}
                />
              </>
            )}
            
            {(selectedDriver === 'both' || selectedDriver === 'LEC') && (
              <>
                <Line 
                  type="monotone" 
                  dataKey="leclerc_time" 
                  stroke="#DC143C" 
                  strokeWidth={3}
                  dot={{ fill: '#DC143C', strokeWidth: 2, r: 4 }}
                  name="Leclerc (Actual)"
                  connectNulls={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="predicted_leclerc" 
                  stroke="#DC143C" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Leclerc (Predicted)"
                  connectNulls={false}
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Key Insights */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Info className="w-5 h-5 text-ferrari-gold" />
            <span className="text-ferrari-white font-bold">OPTIMAL TEMP</span>
          </div>
          <p className="text-2xl font-bold text-ferrari-gold">41-43°C</p>
          <p className="text-ferrari-gray-400 text-sm">Best tire performance window</p>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-ferrari-yellow" />
            <span className="text-ferrari-white font-bold">DEGRADATION</span>
          </div>
          <p className="text-2xl font-bold text-ferrari-yellow">0.045s/lap</p>
          <p className="text-ferrari-gray-400 text-sm">Current tire wear rate</p>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingDown className="w-5 h-5 text-ferrari-red" />
            <span className="text-ferrari-white font-bold">PREDICTION</span>
          </div>
          <p className="text-2xl font-bold text-ferrari-red">±0.2s</p>
          <p className="text-ferrari-gray-400 text-sm">Model accuracy range</p>
        </div>
      </div>
    </div>
  )
}

export default TireDegradationChart 