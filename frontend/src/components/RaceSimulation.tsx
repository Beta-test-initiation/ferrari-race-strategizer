import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Play, Pause, RotateCcw, Settings, TrendingUp, Target } from 'lucide-react'
import apiClient from '../services/api'
import type { RaceSimulationResponse, RaceState } from '../services/api'

interface SimulationScenario {
  id: string
  name: string
  description: string
  strategy_name: string
  pit_lap: number
  new_compound: 'SOFT' | 'MEDIUM' | 'HARD'
  results?: RaceSimulationResponse
}

interface SimulationData {
  lap: number
  hamilton_pos: number
  leclerc_pos: number
  gap_to_leader: number
  points_projection: number
}

const RaceSimulation: React.FC = () => {
  const [raceData, setRaceData] = React.useState<RaceState | null>(null)
  const [isRunning, setIsRunning] = React.useState(false)
  const [selectedScenario, setSelectedScenario] = React.useState<string>('early')
  const [simulationProgress, setSimulationProgress] = React.useState(0)
  const [scenarios, setScenarios] = React.useState<SimulationScenario[]>([])

  const [simulationData, setSimulationData] = React.useState<SimulationData[]>([
    { lap: 5, hamilton_pos: 3, leclerc_pos: 5, gap_to_leader: 8.5, points_projection: 15 },
    { lap: 10, hamilton_pos: 3, leclerc_pos: 5, gap_to_leader: 12.3, points_projection: 15 },
    { lap: 15, hamilton_pos: 2, leclerc_pos: 4, gap_to_leader: 5.8, points_projection: 22 },
    { lap: 20, hamilton_pos: 2, leclerc_pos: 4, gap_to_leader: 8.2, points_projection: 22 },
    { lap: 25, hamilton_pos: 1, leclerc_pos: 3, gap_to_leader: 0.0, points_projection: 33 },
    { lap: 30, hamilton_pos: 1, leclerc_pos: 3, gap_to_leader: 3.4, points_projection: 33 },
  ])

  // Load race data and run simulations for each scenario
  React.useEffect(() => {
    const loadData = async () => {
      try {
        const race = await apiClient.getCurrentRaceState()
        setRaceData(race)

        // Find Ferrari drivers (Leclerc #16, Hamilton #44)
        const ferrariDriver = race.drivers.find(d => d.number === 16 || d.number === 44)
        if (!ferrariDriver) return

        const currentLap = race.current_lap
        const totalLaps = race.total_laps
        const lapsRemaining = totalLaps - currentLap

        // Generate dynamic scenarios based on current race state
        const dynamicScenarios: SimulationScenario[] = [
          {
            id: 'early',
            name: 'Early Pit (Next Lap)',
            description: `Pit immediately to gain advantage. Fresh tires for remaining ${lapsRemaining} laps`,
            strategy_name: 'AGGRESSIVE_UNDERCUT',
            pit_lap: currentLap + 1,
            new_compound: ferrariDriver.tire_compound === 'SOFT' ? 'MEDIUM' : 'SOFT',
          },
          {
            id: 'mid',
            name: 'Mid-Strategy Pit',
            description: `Pit in 5 laps to optimize tire wear and track position`,
            strategy_name: 'DYNAMIC_POSITION_PLAY',
            pit_lap: currentLap + 5,
            new_compound: ferrariDriver.tire_compound === 'HARD' ? 'MEDIUM' : 'HARD',
          },
          {
            id: 'late',
            name: 'Extended Stint',
            description: `Push current tires longer for late-race advantage`,
            strategy_name: 'CONSERVATIVE_LONG_STINT',
            pit_lap: currentLap + 10,
            new_compound: ferrariDriver.tire_compound === 'SOFT' ? 'HARD' : 'SOFT',
          },
        ]

        // Run simulations for each scenario
        const updatedScenarios = await Promise.all(
          dynamicScenarios.map(async (scenario) => {
            try {
              const result = await apiClient.simulateRace({
                race_state: {
                  current_lap: race.current_lap,
                  position: ferrariDriver.position,
                  tire_age: ferrariDriver.tire_age,
                  compound: ferrariDriver.tire_compound as 'SOFT' | 'MEDIUM' | 'HARD',
                  track_temp: race.track_temp,
                  track_id: 1,
                  driver: ferrariDriver.name,
                  gaps_ahead: [],
                  gaps_behind: race.drivers.filter(d => d.position > ferrariDriver.position).slice(0, 3).map(d => d.gap_to_leader),
                  total_laps: race.total_laps,
                },
                strategy_name: scenario.strategy_name,
                pit_lap: scenario.pit_lap,
                new_compound: scenario.new_compound,
                num_simulations: 100,
              })
              return { ...scenario, results: result }
            } catch (err) {
              console.error(`Failed to simulate ${scenario.name}:`, err)
              return scenario
            }
          })
        )
        setScenarios(updatedScenarios)
        setSelectedScenario('mid') // Default to mid-strategy
      } catch (err) {
        console.error('Failed to load race data:', err)
      }
    }

    loadData()
    const interval = setInterval(loadData, 15000) // Refresh every 15 seconds

    return () => clearInterval(interval)
  }, [])

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
    if (probability >= 0.7) return 'text-ferrari-gold'
    if (probability >= 0.5) return 'text-ferrari-yellow'
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

  const selectedScenarioData = scenarios.find(s => s.id === selectedScenario)
  const winProb = selectedScenarioData?.results?.win_probability ?? 0
  const pointsExp = selectedScenarioData?.results?.points_expected ?? 0

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
                {scenario.results && (
                  <span className={`font-bold ${getProbabilityColor(scenario.results.win_probability)}`}>
                    {(scenario.results.win_probability * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              <p className="text-ferrari-gray-400 text-sm mb-3">{scenario.description}</p>

              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-ferrari-gray-400">Pit Lap:</p>
                  <p className="text-ferrari-white font-bold">{scenario.pit_lap}</p>
                </div>
                <div>
                  <p className="text-ferrari-gray-400">Tire:</p>
                  <p className="text-ferrari-white font-bold">{scenario.new_compound}</p>
                </div>
                <div>
                  <p className="text-ferrari-gray-400">Points:</p>
                  <p className="text-ferrari-gold font-bold">
                    {scenario.results ? `+${scenario.results.points_expected.toFixed(0)}` : '--'}
                  </p>
                </div>
                <div>
                  <p className="text-ferrari-gray-400">Podium:</p>
                  <p className="text-ferrari-white font-bold">
                    {scenario.results ? `${(scenario.results.podium_probability * 100).toFixed(0)}%` : '--'}
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
            {(winProb * 100).toFixed(0)}%
          </p>
        </div>

        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Target className="w-5 h-5 text-ferrari-red" />
            <span className="text-ferrari-white font-bold">POINTS GAIN</span>
          </div>
          <p className="text-3xl font-bold text-ferrari-red">
            +{pointsExp.toFixed(0)}
          </p>
        </div>

        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-ferrari-yellow" />
            <span className="text-ferrari-white font-bold">PODIUM CHANCE</span>
          </div>
          <p className="text-3xl font-bold text-ferrari-yellow">
            {selectedScenarioData?.results ? `${(selectedScenarioData.results.podium_probability * 100).toFixed(0)}%` : '--'}
          </p>
        </div>

        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Settings className="w-5 h-5 text-ferrari-silver" />
            <span className="text-ferrari-white font-bold">SIMULATIONS</span>
          </div>
          <p className="text-3xl font-bold text-ferrari-silver">100</p>
        </div>
      </div>
    </div>
  )
}

export default RaceSimulation
