import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingDown, Info, AlertTriangle } from 'lucide-react'
import apiClient from '../services/api'
import type { DegradationPredictionResponse } from '../services/api'

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
  const [degradation, setDegradation] = React.useState<DegradationPredictionResponse | null>(null)
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

  // Load degradation prediction from backend
  React.useEffect(() => {
    const loadDegradation = async () => {
      try {
        const prediction = await apiClient.predictDegradation({
          track_temp: 35.0,
          compound: 'MEDIUM',
          stint_length: 20,
          track_id: 1,
          driver: 'HAM',
        })
        setDegradation(prediction)
      } catch (err) {
        console.error('Failed to load degradation prediction:', err)
      }
    }

    loadDegradation()
    const interval = setInterval(loadDegradation, 10000) // Refresh every 10 seconds

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
        <div className="text-right">
          <p className="text-ferrari-gray-400 text-sm">DEGRADATION RATE</p>
          <p className="text-ferrari-white font-bold text-lg">
            {degradation ? `${degradation.degradation_rate.toFixed(3)}s/lap` : '--'}
          </p>
        </div>
      </div>

      {/* Driver & Metric Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-ferrari-gray-400 text-sm mb-2">SELECT DRIVER</p>
          <div className="flex space-x-2">
            {(['both', 'HAM', 'LEC'] as const).map((driver) => (
              <button
                key={driver}
                onClick={() => handleDriverChange(driver)}
                className={`px-3 py-2 rounded-lg font-bold transition-colors ${
                  selectedDriver === driver
                    ? 'bg-ferrari-red text-ferrari-white'
                    : 'bg-ferrari-gray-700 text-ferrari-gray-400 hover:bg-ferrari-gray-600'
                }`}
              >
                {driver}
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-ferrari-gray-400 text-sm mb-2">METRIC</p>
          <div className="flex space-x-2">
            {(['lap_time', 'degradation'] as const).map((metric) => (
              <button
                key={metric}
                onClick={() => handleMetricChange(metric)}
                className={`px-3 py-2 rounded-lg font-bold transition-colors text-sm ${
                  selectedMetric === metric
                    ? 'bg-ferrari-red text-ferrari-white'
                    : 'bg-ferrari-gray-700 text-ferrari-gray-400 hover:bg-ferrari-gray-600'
                }`}
              >
                {metric === 'lap_time' ? 'Lap Time' : 'Degradation'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={tireData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="lap"
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF' }}
            />
            <YAxis
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF' }}
              domain={['dataMin - 1', 'dataMax + 1']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {selectedDriver !== 'LEC' && (
              <>
                <Line
                  type="monotone"
                  dataKey="hamilton_time"
                  stroke="#FFD700"
                  strokeWidth={2}
                  name="Hamilton (Actual)"
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="predicted_hamilton"
                  stroke="#FFD700"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Hamilton (Predicted)"
                />
              </>
            )}
            {selectedDriver !== 'HAM' && (
              <>
                <Line
                  type="monotone"
                  dataKey="leclerc_time"
                  stroke="#DC143C"
                  strokeWidth={2}
                  name="Leclerc (Actual)"
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="predicted_leclerc"
                  stroke="#DC143C"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Leclerc (Predicted)"
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Degradation Info */}
      {degradation && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-ferrari-gray-900 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingDown className="w-5 h-5 text-ferrari-yellow" />
              <span className="text-ferrari-white font-bold">DEGRADATION RATE</span>
            </div>
            <p className="text-2xl font-bold text-ferrari-yellow">
              {degradation.degradation_rate.toFixed(4)}s/lap
            </p>
          </div>

          <div className="bg-ferrari-gray-900 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-ferrari-red" />
              <span className="text-ferrari-white font-bold">RISK LEVEL</span>
            </div>
            <p className="text-2xl font-bold text-ferrari-red">
              {degradation.risk_level}
            </p>
          </div>

          <div className="bg-ferrari-gray-900 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Info className="w-5 h-5 text-ferrari-gold" />
              <span className="text-ferrari-white font-bold">STINT DURATION</span>
            </div>
            <p className="text-2xl font-bold text-ferrari-gold">
              {degradation.estimated_stint_duration} laps
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default TireDegradationChart
