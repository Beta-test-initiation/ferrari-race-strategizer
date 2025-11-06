import React from 'react'
import { Cloud, Sun, CloudRain, Wind, Thermometer, Droplets } from 'lucide-react'

interface WeatherData {
  current: {
    temperature: number
    humidity: number
    windSpeed: number
    precipitation: number
    conditions: 'sunny' | 'cloudy' | 'rainy' | 'overcast'
    pressure: number
  }
  forecast: {
    time: string
    temp: number
    conditions: string
    rainChance: number
    impact: 'LOW' | 'MEDIUM' | 'HIGH'
  }[]
  trackImpact: {
    gripLevel: number
    tireWear: number
    degradationRate: number
    recommendedCompound: 'SOFT' | 'MEDIUM' | 'HARD' | 'INTERMEDIATE' | 'WET'
    strategyChange: string
  }
}

const WeatherImpact: React.FC = () => {
  const [weatherData, setWeatherData] = React.useState<WeatherData>({
    current: {
      temperature: 28,
      humidity: 65,
      windSpeed: 12,
      precipitation: 0,
      conditions: 'sunny',
      pressure: 1013
    },
    forecast: [
      { time: '14:00', temp: 29, conditions: 'Sunny', rainChance: 5, impact: 'LOW' },
      { time: '15:00', temp: 30, conditions: 'Partly Cloudy', rainChance: 15, impact: 'LOW' },
      { time: '16:00', temp: 28, conditions: 'Cloudy', rainChance: 35, impact: 'MEDIUM' },
      { time: '17:00', temp: 26, conditions: 'Light Rain', rainChance: 70, impact: 'HIGH' },
      { time: '18:00', temp: 24, conditions: 'Rain', rainChance: 85, impact: 'HIGH' },
    ],
    trackImpact: {
      gripLevel: 85,
      tireWear: 1.2,
      degradationRate: 0.045,
      recommendedCompound: 'MEDIUM',
      strategyChange: 'Standard strategy optimal'
    }
  })

  // TODO: Implement real-time weather updates from weather API
  React.useEffect(() => {
    const interval = setInterval(() => {
      setWeatherData(prev => ({
        ...prev,
        current: {
          ...prev.current,
          temperature: prev.current.temperature + (Math.random() - 0.5) * 2,
          humidity: Math.max(30, Math.min(90, prev.current.humidity + (Math.random() - 0.5) * 10)),
          windSpeed: Math.max(0, prev.current.windSpeed + (Math.random() - 0.5) * 5)
        }
      }))
    }, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const getWeatherIcon = (conditions: string) => {
    switch (conditions.toLowerCase()) {
      case 'sunny':
        return <Sun className="w-6 h-6 text-ferrari-yellow" />
      case 'cloudy':
      case 'partly cloudy':
      case 'overcast':
        return <Cloud className="w-6 h-6 text-ferrari-gray-400" />
      case 'rainy':
      case 'light rain':
      case 'rain':
        return <CloudRain className="w-6 h-6 text-ferrari-blue" />
      default:
        return <Sun className="w-6 h-6 text-ferrari-yellow" />
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
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

  const getRainChanceColor = (chance: number) => {
    if (chance >= 70) return 'text-ferrari-red'
    if (chance >= 40) return 'text-ferrari-yellow'
    return 'text-ferrari-gold'
  }

  const getTireColor = (tire: string) => {
    switch (tire) {
      case 'SOFT':
        return 'bg-ferrari-red text-ferrari-white'
      case 'MEDIUM':
        return 'bg-ferrari-yellow text-ferrari-black'
      case 'HARD':
        return 'bg-ferrari-white text-ferrari-black'
      case 'INTERMEDIATE':
        return 'bg-ferrari-gold text-ferrari-black'
      case 'WET':
        return 'bg-ferrari-blue text-ferrari-white'
      default:
        return 'bg-ferrari-gray-500 text-ferrari-white'
    }
  }

  const getGripColor = (grip: number) => {
    if (grip >= 80) return 'text-ferrari-gold'
    if (grip >= 60) return 'text-ferrari-yellow'
    return 'text-ferrari-red'
  }

  return (
    <div className="dashboard-panel p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-ferrari-white flex items-center">
          <Cloud className="w-6 h-6 mr-2 text-ferrari-red" />
          WEATHER IMPACT
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-ferrari-gold rounded-full animate-pulse"></div>
          <span className="text-ferrari-gray-400 text-sm">LIVE</span>
        </div>
      </div>

      {/* Current Conditions */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-ferrari-white mb-3">CURRENT CONDITIONS</h3>
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              {getWeatherIcon(weatherData.current.conditions)}
              <div>
                <p className="text-ferrari-white font-bold capitalize">
                  {weatherData.current.conditions}
                </p>
                <p className="text-ferrari-gray-400 text-sm">Track conditions</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-ferrari-white">
                {weatherData.current.temperature.toFixed(1)}°C
              </p>
              <p className="text-ferrari-gray-400 text-sm">Air temperature</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <Droplets className="w-4 h-4 text-ferrari-gray-400" />
                <span className="text-ferrari-gray-400 text-sm">HUMIDITY</span>
              </div>
              <p className="text-ferrari-white font-bold">{weatherData.current.humidity}%</p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <Wind className="w-4 h-4 text-ferrari-gray-400" />
                <span className="text-ferrari-gray-400 text-sm">WIND</span>
              </div>
              <p className="text-ferrari-white font-bold">{weatherData.current.windSpeed.toFixed(1)} km/h</p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <CloudRain className="w-4 h-4 text-ferrari-gray-400" />
                <span className="text-ferrari-gray-400 text-sm">RAIN</span>
              </div>
              <p className="text-ferrari-white font-bold">{weatherData.current.precipitation.toFixed(1)} mm</p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <Thermometer className="w-4 h-4 text-ferrari-gray-400" />
                <span className="text-ferrari-gray-400 text-sm">PRESSURE</span>
              </div>
              <p className="text-ferrari-white font-bold">{weatherData.current.pressure} hPa</p>
            </div>
          </div>
        </div>
      </div>

      {/* Forecast */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-ferrari-white mb-3">RACE FORECAST</h3>
        <div className="space-y-2">
          {weatherData.forecast.map((item, index) => (
            <div key={index} className="bg-ferrari-gray-900 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 text-center">
                    <p className="text-ferrari-white font-bold">{item.time}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getWeatherIcon(item.conditions)}
                    <span className="text-ferrari-white text-sm">{item.conditions}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-center">
                    <p className="text-ferrari-gray-400 text-xs">TEMP</p>
                    <p className="text-ferrari-white font-bold">{item.temp}°C</p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-ferrari-gray-400 text-xs">RAIN</p>
                    <p className={`font-bold ${getRainChanceColor(item.rainChance)}`}>
                      {item.rainChance}%
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-ferrari-gray-400 text-xs">IMPACT</p>
                    <p className={`font-bold text-sm ${getImpactColor(item.impact)}`}>
                      {item.impact}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Track Impact */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-ferrari-white">TRACK IMPACT</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-ferrari-gray-900 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-3 h-3 bg-ferrari-gold rounded-full"></div>
              <span className="text-ferrari-white font-bold">GRIP LEVEL</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-ferrari-gray-700 rounded-full h-2">
                <div
                  className="bg-ferrari-gold h-2 rounded-full transition-all duration-300"
                  style={{ width: `${weatherData.trackImpact.gripLevel}%` }}
                ></div>
              </div>
              <span className={`font-bold ${getGripColor(weatherData.trackImpact.gripLevel)}`}>
                {weatherData.trackImpact.gripLevel}%
              </span>
            </div>
          </div>
          
          <div className="bg-ferrari-gray-900 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-3 h-3 bg-ferrari-red rounded-full"></div>
              <span className="text-ferrari-white font-bold">TIRE WEAR</span>
            </div>
            <p className="text-2xl font-bold text-ferrari-red">
              {weatherData.trackImpact.tireWear.toFixed(1)}x
            </p>
            <p className="text-ferrari-gray-400 text-sm">vs normal conditions</p>
          </div>
        </div>
        
        <div className="bg-ferrari-gray-900 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-ferrari-yellow rounded-full"></div>
              <span className="text-ferrari-white font-bold">RECOMMENDED COMPOUND</span>
            </div>
            <span className={`px-3 py-1 rounded font-bold ${getTireColor(weatherData.trackImpact.recommendedCompound)}`}>
              {weatherData.trackImpact.recommendedCompound}
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-ferrari-gray-400 text-sm mb-1">DEGRADATION RATE</p>
              <p className="text-ferrari-white font-bold">
                {weatherData.trackImpact.degradationRate.toFixed(3)}s/lap
              </p>
            </div>
            <div>
              <p className="text-ferrari-gray-400 text-sm mb-1">STRATEGY IMPACT</p>
              <p className="text-ferrari-white font-bold text-sm">
                {weatherData.trackImpact.strategyChange}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Weather Alerts */}
      <div className="mt-6 p-3 bg-ferrari-gray-900 rounded-lg border-l-4 border-ferrari-yellow">
        <div className="flex items-center space-x-2">
          <CloudRain className="w-5 h-5 text-ferrari-yellow" />
          <span className="text-ferrari-white font-bold">WEATHER ALERT</span>
        </div>
        <p className="text-ferrari-gray-300 text-sm mt-1">
          Rain expected in 2 hours. Consider intermediate tire strategy for final stint.
        </p>
      </div>
    </div>
  )
}

export default WeatherImpact 