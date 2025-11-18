import React from 'react'
import { Zap, Clock, Target, TrendingUp, AlertCircle } from 'lucide-react'
import apiClient from '../services/api'
import type { StrategyRecommendationResponse, RaceState } from '../services/api'

interface CompetitorData {
  name: string
  position: number
  gap: number
  currentTire: 'SOFT' | 'MEDIUM' | 'HARD'
  tireLaps: number
  pitWindow: string
  threat: 'LOW' | 'MEDIUM' | 'HIGH'
}

const PitStopOptimizer: React.FC = () => {
  const [strategy, setStrategy] = React.useState<StrategyRecommendationResponse | null>(null)
  const [raceData, setRaceData] = React.useState<RaceState | null>(null)
  const [competitors, setCompetitors] = React.useState<CompetitorData[]>([])
  const [loading, setLoading] = React.useState(true)

  // Load race data and strategy recommendation
  React.useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)

        // Get race data to extract competitor information
        const race = await apiClient.getCurrentRaceState()
        setRaceData(race)

        // Convert race drivers (excluding first 2) to competitors
        const competitorList: CompetitorData[] = race.drivers.slice(2).map(driver => ({
          name: driver.name,
          position: driver.position,
          gap: driver.gap_to_leader,
          currentTire: driver.tire_compound as 'SOFT' | 'MEDIUM' | 'HARD',
          tireLaps: driver.tire_age,
          pitWindow: 'LAP 35-40', // Could come from strategy engine
          threat: driver.gap_to_leader < 3 ? 'HIGH' : driver.gap_to_leader < 8 ? 'MEDIUM' : 'LOW',
        }))
        setCompetitors(competitorList)

        // Get strategy recommendation for first driver (HAM)
        const firstDriver = race.drivers[0]
        const recommendation = await apiClient.getStrategyRecommendation({
          current_lap: race.current_lap,
          position: firstDriver.position,
          tire_age: firstDriver.tire_age,
          compound: firstDriver.tire_compound as 'SOFT' | 'MEDIUM' | 'HARD',
          track_temp: race.track_temp,
          track_id: 1,
          driver: 'HAM',
          gaps_ahead: [],
          gaps_behind: race.drivers.slice(1, 3).map(d => d.gap_to_leader),
          total_laps: race.total_laps,
        })
        setStrategy(recommendation)
      } catch (error) {
        console.error('Failed to load optimizer data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
    const interval = setInterval(loadData, 10000)

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

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-ferrari-gold'
    if (confidence >= 60) return 'text-ferrari-yellow'
    return 'text-ferrari-red'
  }

  const getThreatColor = (threat: string) => {
    switch (threat) {
      case 'HIGH':
        return 'text-ferrari-red'
      case 'MEDIUM':
        return 'text-ferrari-yellow'
      case 'LOW':
        return 'text-ferrari-gold'
      default:
        return 'text-ferrari-gray-400'
    }
  }

  const getUrgencyStatus = (optimalLap: number, currentLap: number) => {
    const lapsToOptimal = optimalLap - currentLap
    if (lapsToOptimal <= 2) return { status: 'CRITICAL', color: 'text-ferrari-red animate-flash' }
    if (lapsToOptimal <= 5) return { status: 'WARNING', color: 'text-ferrari-yellow' }
    return { status: 'MONITOR', color: 'text-ferrari-gold' }
  }

  if (loading && !strategy) {
    return (
      <div className="dashboard-panel p-6 text-center">
        <p className="text-ferrari-gray-400">Loading pit optimizer...</p>
      </div>
    )
  }

  return (
    <div className="dashboard-panel p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-ferrari-white flex items-center">
          <Zap className="w-6 h-6 mr-2 text-ferrari-red" />
          PIT STOP OPTIMIZER
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-ferrari-yellow rounded-full animate-pulse"></div>
          <span className="text-ferrari-gray-400 text-sm">ACTIVE</span>
        </div>
      </div>

      {/* Strategy Recommendation */}
      {strategy && (
        <div className="space-y-4 mb-6">
          <h3 className="text-lg font-bold text-ferrari-white">RECOMMENDATION</h3>
          <div className="bg-ferrari-gray-900 rounded-lg p-4 border-l-4 border-ferrari-red">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-ferrari-white font-bold text-lg">
                  {strategy.immediate_action.recommendation}
                </p>
                <p className="text-ferrari-gray-400 text-sm mt-1">
                  {strategy.immediate_action.reason}
                </p>
              </div>
              <div className="text-right">
                <p className={`font-bold text-lg ${getConfidenceColor(strategy.immediate_action.confidence)}`}>
                  {strategy.immediate_action.confidence}%
                </p>
                <p className="text-ferrari-gray-400 text-sm">Confidence</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">OPTIMAL LAP</p>
                <p className="text-ferrari-white font-bold text-xl">
                  {strategy.optimal_strategy.pit_lap}
                </p>
              </div>

              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">TIME GAIN</p>
                <p className="text-ferrari-gold font-bold text-xl">
                  +{strategy.optimal_strategy.expected_time_gain.toFixed(1)}s
                </p>
              </div>

              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">POSITION GAIN</p>
                <p className="text-ferrari-white font-bold text-xl">
                  +{strategy.optimal_strategy.expected_position_gain.toFixed(1)}
                </p>
              </div>

              <div className="text-center">
                <p className="text-ferrari-gray-400 text-sm">TIRE REC</p>
                <span className={`px-2 py-1 rounded font-bold text-sm ${getTireColor(strategy.optimal_strategy.new_compound)}`}>
                  {strategy.optimal_strategy.new_compound}
                </span>
              </div>
            </div>

            {strategy.optimal_strategy.weather_impact && (
              <div className="mt-3 pt-3 border-t border-ferrari-gray-700">
                <p className="text-ferrari-gray-300 text-sm">
                  <strong>Weather:</strong> {strategy.optimal_strategy.weather_impact}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Competitor Analysis */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-ferrari-white">COMPETITOR ANALYSIS</h3>
        {competitors.length > 0 ? (
          <div className="space-y-2">
            {competitors.map((comp, index) => (
              <div key={index} className="bg-ferrari-gray-900 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-ferrari-gray-600 flex items-center justify-center">
                      <span className="text-ferrari-white font-bold text-sm">P{comp.position}</span>
                    </div>
                    <div>
                      <p className="text-ferrari-white font-bold">{comp.name}</p>
                      <p className="text-ferrari-gray-400 text-sm">
                        {comp.gap > 0 ? `+${comp.gap.toFixed(1)}s` : `${comp.gap.toFixed(1)}s`}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <p className="text-ferrari-gray-400 text-xs">TIRE</p>
                      <div className="flex items-center space-x-1">
                        <span className={`px-1 py-0.5 rounded font-bold text-xs ${getTireColor(comp.currentTire)}`}>
                          {comp.currentTire}
                        </span>
                        <span className="text-ferrari-white text-xs">{comp.tireLaps}</span>
                      </div>
                    </div>

                    <div className="text-center">
                      <p className="text-ferrari-gray-400 text-xs">THREAT</p>
                      <p className={`font-bold text-xs ${getThreatColor(comp.threat)}`}>
                        {comp.threat}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-ferrari-gray-400">No competitors detected</p>
        )}
      </div>

      {/* Quick Actions */}
      <div className="mt-6 flex flex-wrap gap-2">
        <button className="ferrari-button flex items-center space-x-2">
          <Target className="w-4 h-4" />
          <span>EXECUTE PIT</span>
        </button>
        <button className="bg-ferrari-gray-700 hover:bg-ferrari-gray-600 text-ferrari-white font-bold py-2 px-4 rounded-lg transition-colors">
          <Clock className="w-4 h-4 inline mr-2" />
          DELAY 2 LAPS
        </button>
        <button className="bg-ferrari-gray-700 hover:bg-ferrari-gray-600 text-ferrari-white font-bold py-2 px-4 rounded-lg transition-colors">
          <TrendingUp className="w-4 h-4 inline mr-2" />
          SIMULATE
        </button>
      </div>
    </div>
  )
}

export default PitStopOptimizer
