import React from 'react'
import { Zap, Clock, Target, TrendingUp, AlertCircle } from 'lucide-react'

interface PitWindow {
  driver: 'HAM' | 'LEC'
  optimalLap: number
  currentLap: number
  timeGain: number
  confidence: number
  reason: string
  tireRecommendation: 'SOFT' | 'MEDIUM' | 'HARD'
  weatherImpact: 'NONE' | 'SLIGHT' | 'MODERATE' | 'HIGH'
  trackPosition: number
}

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
  const [currentLap, setCurrentLap] = React.useState(32)
  const [pitRecommendations, setPitRecommendations] = React.useState<PitWindow[]>([
    {
      driver: 'HAM',
      optimalLap: 36,
      currentLap: 32,
      timeGain: 8.5,
      confidence: 85,
      reason: 'Undercut opportunity vs Norris',
      tireRecommendation: 'HARD',
      weatherImpact: 'NONE',
      trackPosition: 3
    },
    {
      driver: 'LEC',
      optimalLap: 42,
      currentLap: 32,
      timeGain: 12.3,
      confidence: 78,
      reason: 'Optimal tire wear window',
      tireRecommendation: 'HARD',
      weatherImpact: 'SLIGHT',
      trackPosition: 5
    }
  ])

  const [competitors, setCompetitors] = React.useState<CompetitorData[]>([
    { name: 'Norris', position: 2, gap: -5.2, currentTire: 'MEDIUM', tireLaps: 18, pitWindow: 'LAP 34-38', threat: 'HIGH' },
    { name: 'Russell', position: 4, gap: +2.8, currentTire: 'MEDIUM', tireLaps: 16, pitWindow: 'LAP 36-40', threat: 'MEDIUM' },
    { name: 'Piastri', position: 6, gap: +8.1, currentTire: 'HARD', tireLaps: 22, pitWindow: 'LAP 45-50', threat: 'LOW' },
    { name: 'Sainz', position: 7, gap: +12.5, currentTire: 'MEDIUM', tireLaps: 19, pitWindow: 'LAP 35-39', threat: 'MEDIUM' }
  ])

  // TODO: Implement real-time pit strategy updates from ML backend
  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentLap(prev => prev + 1)
      
      setPitRecommendations(prev => prev.map(rec => ({
        ...rec,
        currentLap: rec.currentLap + 1,
        timeGain: rec.timeGain + (Math.random() - 0.5) * 2,
        confidence: Math.max(50, Math.min(95, rec.confidence + (Math.random() - 0.5) * 10))
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

      {/* Pit Recommendations */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-bold text-ferrari-white">PIT RECOMMENDATIONS</h3>
        {pitRecommendations.map((rec) => {
          const urgency = getUrgencyStatus(rec.optimalLap, rec.currentLap)
          const lapsToOptimal = rec.optimalLap - rec.currentLap
          
          return (
            <div key={rec.driver} className="bg-ferrari-gray-900 rounded-lg p-4 border-l-4 border-ferrari-red">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                    rec.driver === 'HAM' ? 'bg-ferrari-gold text-ferrari-black' : 'bg-ferrari-red text-ferrari-white'
                  }`}>
                    {rec.driver}
                  </div>
                  <div>
                    <p className="text-ferrari-white font-bold">
                      {rec.driver === 'HAM' ? 'Lewis Hamilton' : 'Charles Leclerc'}
                    </p>
                    <p className="text-ferrari-gray-400 text-sm">Position {rec.trackPosition}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-bold text-lg ${urgency.color}`}>
                    {urgency.status}
                  </p>
                  <p className="text-ferrari-gray-400 text-sm">
                    {lapsToOptimal > 0 ? `${lapsToOptimal} laps` : 'NOW'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-ferrari-gray-400 text-sm">OPTIMAL LAP</p>
                  <p className="text-ferrari-white font-bold text-xl">{rec.optimalLap}</p>
                </div>
                
                <div className="text-center">
                  <p className="text-ferrari-gray-400 text-sm">TIME GAIN</p>
                  <p className="text-ferrari-gold font-bold text-xl">+{rec.timeGain.toFixed(1)}s</p>
                </div>
                
                <div className="text-center">
                  <p className="text-ferrari-gray-400 text-sm">CONFIDENCE</p>
                  <p className={`font-bold text-xl ${getConfidenceColor(rec.confidence)}`}>
                    {rec.confidence}%
                  </p>
                </div>
                
                <div className="text-center">
                  <p className="text-ferrari-gray-400 text-sm">TIRE REC</p>
                  <span className={`px-2 py-1 rounded font-bold text-sm ${getTireColor(rec.tireRecommendation)}`}>
                    {rec.tireRecommendation}
                  </span>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-ferrari-gray-700">
                <p className="text-ferrari-gray-300 text-sm">
                  <strong>Strategy:</strong> {rec.reason}
                </p>
                {rec.weatherImpact !== 'NONE' && (
                  <p className="text-ferrari-yellow text-sm mt-1">
                    <AlertCircle className="w-4 h-4 inline mr-1" />
                    Weather impact: {rec.weatherImpact}
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Competitor Analysis */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-ferrari-white">COMPETITOR ANALYSIS</h3>
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
                    <p className="text-ferrari-gray-400 text-xs">PIT WINDOW</p>
                    <p className="text-ferrari-white text-xs font-mono">{comp.pitWindow}</p>
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