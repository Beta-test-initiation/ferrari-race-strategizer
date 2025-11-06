import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Play, Pause, RotateCcw, Settings, TrendingUp, Target } from 'lucide-react'

interface SimulationScenario {
  id: string
  name: string
  description: string
  parameters: {
    hamPitLap: number
    lecPitLap: number
    hamTireStrategy: string
    lecTireStrategy: string
    weatherChange: boolean
    safetyCarRisk: number
  }
  results: {
    hamFinalPosition: number
    lecFinalPosition: number
    hamRaceTime: string
    lecRaceTime: string
    probability: number
    pointsGained: number
  }
}

interface SimulationData {
  lap: number
  hamilton_pos: number
  leclerc_pos: number
  gap_to_leader: number
  points_projection: number
}

const RaceSimulation: React.FC = () => {
  const [isRunning, setIsRunning] = React.useState(false)
  const [selectedScenario, setSelectedScenario] = React.useState<string>('aggressive')
  const [simulationProgress, setSimulationProgress] = React.useState(0)
  
  const [scenarios, setScenarios] = React.useState<SimulationScenario[]>([
    {
      id: 'aggressive',
      name: 'Aggressive Undercut',
      description: 'Early pit stops to gain track position',
      parameters: {
        hamPitLap: 18,
        lecPitLap: 20,
        hamTireStrategy: 'M-S-H',
        lecTireStrategy: 'M-S-H',
        weatherChange: false,
        safetyCarRisk: 0.15
      },
      results: {
        hamFinalPosition: 2,
        lecFinalPosition: 4,
        hamRaceTime: '1:28:45.234',
        lecRaceTime: '1:28:52.678',
        probability: 68,
        pointsGained: 25
      }
    },
    {
      id: 'conservative',
      name: 'Conservative Long Stint',
      description: 'Extended first stint for better tire window',
      parameters: {
        hamPitLap: 35,
        lecPitLap: 37,
        hamTireStrategy: 'M-H',
        lecTireStrategy: 'M-H',
        weatherChange: false,
        safetyCarRisk: 0.20
      },
      results: {
        hamFinalPosition: 3,
        lecFinalPosition: 5,
        hamRaceTime: '1:28:48.567',
        lecRaceTime: '1:28:55.123',
        probability: 78,
        pointsGained: 18
      }
    },
    {
      id: 'weather',
      name: 'Weather Reactive',
      description: 'Strategy adapted for rain probability',
      parameters: {
        hamPitLap: 25,
        lecPitLap: 27,
        hamTireStrategy: 'M-I-W',
        lecTireStrategy: 'M-I-W',
        weatherChange: true,
        safetyCarRisk: 0.40
      },
      results: {
        hamFinalPosition: 1,
        lecFinalPosition: 3,
        hamRaceTime: '1:28:42.890',
        lecRaceTime: '1:28:48.234',
        probability: 45,
        pointsGained: 33
      }
    }
  ])

  const [simulationData, setSimulationData] = React.useState<SimulationData[]>([
    { lap: 5, hamilton_pos: 3, leclerc_pos: 5, gap_to_leader: 8.5, points_projection: 15 },
    { lap: 10, hamilton_pos: 3, leclerc_pos: 5, gap_to_leader: 12.3, points_projection: 15 },
    { lap: 15, hamilton_pos: 2, leclerc_pos: 4, gap_to_leader: 5.8, points_projection: 22 },
    { lap: 20, hamilton_pos: 2, leclerc_pos: 4, gap_to_leader: 8.2, points_projection: 22 },
    { lap: 25, hamilton_pos: 1, leclerc_pos: 3, gap_to_leader: 0.0, points_projection: 33 },
    { lap: 30, hamilton_pos: 1, leclerc_pos: 3, gap_to_leader: 3.4, points_projection: 33 },
    { lap: 35, hamilton_pos: 1, leclerc_pos: 3, gap_to_leader: 6.7, points_projection: 33 },
    { lap: 40, hamilton_pos: 2, leclerc_pos: 4, gap_to_leader: 2.1, points_projection: 25 },
  ])

  // TODO: Implement real-time simulation from ML backend
  const handleRunSimulation = () => {
    setIsRunning(true)
    setSimulationProgress(0)
    
    const interval = setInterval(() => {
      setSimulationProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsRunning(false)
          return 100
        }
        return prev + 10
      })
    }, 200)
  }

  const handleResetSimulation = () => {
    setIsRunning(false)
    setSimulationProgress(0)
  }

  const getPositionColor = (position: number) => {
    if (position === 1) return 'text-ferrari-gold'
    if (position <= 3) return 'text-ferrari-silver'
    if (position <= 10) return 'text-ferrari-white'
    return 'text-ferrari-gray-400'
  }

  const getProbabilityColor = (probability: number) => {
    if (probability >= 70) return 'text-ferrari-gold'
    if (probability >= 50) return 'text-ferrari-yellow'
    return 'text-ferrari-red'
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-ferrari-gray-900 border border-ferrari-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-ferrari-white font-bold mb-2">LAP {label}</p>
          <div className="space-y-1">
            <p className="text-ferrari-gold text-sm">
              Hamilton: P{payload[0]?.payload?.hamilton_pos}
            </p>
            <p className="text-ferrari-red text-sm">
              Leclerc: P{payload[0]?.payload?.leclerc_pos}
            </p>
            <p className="text-ferrari-white text-sm">
              Gap to Leader: {payload[0]?.payload?.gap_to_leader?.toFixed(1)}s
            </p>
            <p className="text-ferrari-gray-400 text-sm">
              Points Projection: {payload[0]?.payload?.points_projection}
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="dashboard-panel p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-ferrari-white flex items-center">
          <Target className="w-6 h-6 mr-2 text-ferrari-red" />
          RACE SIMULATION
        </h2>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            isRunning ? 'bg-ferrari-red animate-pulse' : 'bg-ferrari-gray-500'
          }`}></div>
          <span className="text-ferrari-gray-400 text-sm">
            {isRunning ? 'RUNNING' : 'READY'}
          </span>
        </div>
      </div>

      {/* Scenario Selection */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-bold text-ferrari-white">SCENARIOS</h3>
          <button className="bg-ferrari-gray-700 hover:bg-ferrari-gray-600 text-ferrari-white p-2 rounded-lg transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selectedScenario === scenario.id
                  ? 'border-ferrari-red bg-ferrari-gray-900'
                  : 'border-ferrari-gray-700 bg-ferrari-gray-800 hover:border-ferrari-gray-600'
              }`}
              onClick={() => setSelectedScenario(scenario.id)}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-ferrari-white font-bold">{scenario.name}</h4>
                <span className={`font-bold ${getProbabilityColor(scenario.results.probability)}`}>
                  {scenario.results.probability}%
                </span>
              </div>
              <p className="text-ferrari-gray-400 text-sm mb-3">{scenario.description}</p>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-ferrari-gray-400">HAM Final:</p>
                  <p className={`font-bold ${getPositionColor(scenario.results.hamFinalPosition)}`}>
                    P{scenario.results.hamFinalPosition}
                  </p>
                </div>
                <div>
                  <p className="text-ferrari-gray-400">LEC Final:</p>
                  <p className={`font-bold ${getPositionColor(scenario.results.lecFinalPosition)}`}>
                    P{scenario.results.lecFinalPosition}
                  </p>
                </div>
                <div>
                  <p className="text-ferrari-gray-400">Points:</p>
                  <p className="text-ferrari-gold font-bold">+{scenario.results.pointsGained}</p>
                </div>
                <div>
                  <p className="text-ferrari-gray-400">Strategy:</p>
                  <p className="text-ferrari-white font-bold text-xs">
                    {scenario.parameters.hamTireStrategy}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Simulation Controls */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={handleRunSimulation}
          disabled={isRunning}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-bold transition-colors ${
            isRunning
              ? 'bg-ferrari-gray-600 text-ferrari-gray-400 cursor-not-allowed'
              : 'ferrari-button'
          }`}
        >
          {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          <span>{isRunning ? 'RUNNING' : 'RUN SIMULATION'}</span>
        </button>
        
        <button
          onClick={handleResetSimulation}
          className="bg-ferrari-gray-700 hover:bg-ferrari-gray-600 text-ferrari-white font-bold py-2 px-4 rounded-lg transition-colors flex items-center space-x-2"
        >
          <RotateCcw className="w-4 h-4" />
          <span>RESET</span>
        </button>

        {simulationProgress > 0 && (
          <div className="flex-1 max-w-xs">
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-ferrari-gray-700 rounded-full h-2">
                <div
                  className="bg-ferrari-red h-2 rounded-full transition-all duration-300"
                  style={{ width: `${simulationProgress}%` }}
                ></div>
              </div>
              <span className="text-ferrari-white text-sm font-mono">
                {simulationProgress}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Results Chart */}
      <div className="h-80 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={simulationData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
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
              label={{ value: 'Position', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              domain={[0, 10]}
              reversed
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="hamilton_pos" 
              fill="#FFD700" 
              name="Hamilton Position"
              radius={[4, 4, 0, 0]}
            />
            <Bar 
              dataKey="leclerc_pos" 
              fill="#DC143C" 
              name="Leclerc Position"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-ferrari-gold" />
            <span className="text-ferrari-white font-bold">WIN PROBABILITY</span>
          </div>
          <p className="text-3xl font-bold text-ferrari-gold">
            {scenarios.find(s => s.id === selectedScenario)?.results.probability}%
          </p>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Target className="w-5 h-5 text-ferrari-red" />
            <span className="text-ferrari-white font-bold">POINTS GAIN</span>
          </div>
          <p className="text-3xl font-bold text-ferrari-red">
            +{scenarios.find(s => s.id === selectedScenario)?.results.pointsGained}
          </p>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Play className="w-5 h-5 text-ferrari-yellow" />
            <span className="text-ferrari-white font-bold">RISK LEVEL</span>
          </div>
          <p className="text-3xl font-bold text-ferrari-yellow">
            {scenarios.find(s => s.id === selectedScenario)?.parameters.safetyCarRisk 
              ? (scenarios.find(s => s.id === selectedScenario)!.parameters.safetyCarRisk * 100).toFixed(0) + '%'
              : 'LOW'}
          </p>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Settings className="w-5 h-5 text-ferrari-silver" />
            <span className="text-ferrari-white font-bold">SIMULATIONS</span>
          </div>
          <p className="text-3xl font-bold text-ferrari-silver">1,000</p>
        </div>
      </div>
    </div>
  )
}

export default RaceSimulation 