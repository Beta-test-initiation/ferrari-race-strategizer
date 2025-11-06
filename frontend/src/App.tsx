import React from 'react'
import Header from './components/Header'
import StrategyOverview from './components/StrategyOverview'
import TireDegradationChart from './components/TireDegradationChart'
import PitStopOptimizer from './components/PitStopOptimizer'
import RaceSimulation from './components/RaceSimulation'
import WeatherImpact from './components/WeatherImpact'
import LiveAlerts from './components/LiveAlerts'

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-ferrari-black racing-grid">
      <Header />
      
      <main className="container mx-auto px-4 py-6">
        {/* Critical Alerts Section */}
        <div className="mb-6">
          <LiveAlerts />
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {/* Strategy Overview - Full width on large screens */}
          <div className="lg:col-span-2 xl:col-span-3">
            <StrategyOverview />
          </div>

          {/* Tire Analysis */}
          <div className="lg:col-span-1 xl:col-span-2">
            <TireDegradationChart />
          </div>

          {/* Pit Stop Optimizer */}
          <div className="lg:col-span-1 xl:col-span-1">
            <PitStopOptimizer />
          </div>

          {/* Race Simulation */}
          <div className="lg:col-span-1 xl:col-span-2">
            <RaceSimulation />
          </div>

          {/* Weather Impact */}
          <div className="lg:col-span-1 xl:col-span-1">
            <WeatherImpact />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App 