# Ferrari F1 Strategy Dashboard

A professional, real-time strategy dashboard for Ferrari Formula 1 racing operations. Built with React, TypeScript, and Tailwind CSS to provide critical race strategy insights in a sleek, race-pit-worthy interface.

## Features

### Real-Time Strategy Monitoring
- **Live Alerts**: Critical race notifications with driver-specific color coding
- **Strategy Overview**: Complete race status with track conditions and driver performance
- **Tire Degradation Analysis**: Interactive charts showing tire performance with ML predictions
- **Pit Stop Optimizer**: Strategic recommendations with confidence levels and competitor analysis
- **Race Simulation**: What-if scenario analysis with multiple strategy options
- **Weather Impact**: Real-time weather monitoring and strategy adjustments

### Ferrari-Authentic Design
- **Brand Colors**: Official Ferrari red, gold, and black color scheme
- **Racing Typography**: Professional pit-wall aesthetic with Rajdhani font
- **Responsive Layout**: Optimized for both desktop and mobile viewing
- **Live Data Indicators**: Animated status indicators for real-time updates
- **Professional UI**: Clean, modern interface suitable for race operations

## Technology Stack

- **Frontend**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom Ferrari theme
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React icons
- **Build Tool**: Vite for fast development
- **Package Manager**: npm

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ferrari-strategy-maker/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

## Dashboard Components

### 1. Header
- Ferrari branding with live system status
- Real-time clock and connection monitoring
- Race session information

### 2. Live Alerts
- Critical pit window notifications
- Track condition alerts
- Strategy recommendations
- Driver-specific color coding (Hamilton: Gold, Leclerc: Red)

### 3. Strategy Overview
- Current race position and lap information
- Track temperature and weather conditions
- Driver status with tire information
- Gap analysis and pit stop history

### 4. Tire Degradation Chart
- Real-time tire performance visualization
- ML prediction overlay with confidence intervals
- Driver comparison and filtering options
- Temperature correlation analysis

### 5. Pit Stop Optimizer
- Optimal pit window recommendations
- Competitor analysis with threat assessment
- Strategy confidence levels
- Quick action buttons for pit execution

### 6. Race Simulation
- Multiple scenario analysis
- Monte Carlo simulation results
- Risk assessment and probability calculations
- Interactive strategy comparison

### 7. Weather Impact
- Current conditions with detailed metrics
- 5-hour race forecast
- Track impact analysis
- Tire compound recommendations

## Data Integration

The dashboard is designed to integrate with:
- **ML Backend**: Real-time tire degradation predictions
- **Weather API**: Live weather updates
- **F1 Telemetry**: Race data and timing information
- **Strategy Engine**: Pit stop optimization algorithms

## Configuration

### Environment Variables
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_WEATHER_API_KEY=your_weather_api_key
VITE_WEBSOCKET_URL=ws://localhost:8000/ws
```

### Customization
- **Colors**: Modify `tailwind.config.js` for custom Ferrari colors
- **Fonts**: Update font imports in `index.html`
- **Components**: Each component is modular and can be customized independently

## Development

### Project Structure
```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── Header.tsx     # Main header component
│   │   ├── LiveAlerts.tsx # Alert notifications
│   │   ├── StrategyOverview.tsx
│   │   ├── TireDegradationChart.tsx
│   │   ├── PitStopOptimizer.tsx
│   │   ├── RaceSimulation.tsx
│   │   └── WeatherImpact.tsx
│   ├── App.tsx            # Main application
│   ├── main.tsx           # React entry point
│   └── index.css          # Global styles
├── package.json
├── tailwind.config.js     # Tailwind configuration
├── tsconfig.json          # TypeScript configuration
└── vite.config.ts         # Vite configuration
```

### Available Scripts
- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run preview`: Preview production build
- `npm run lint`: Run ESLint

## Production Deployment

### Build Optimization
```bash
npm run build
```

### Deployment Options
- **Netlify**: Connect to your git repository
- **Vercel**: Deploy with automatic CI/CD
- **AWS S3**: Static website hosting
- **Docker**: Use provided Dockerfile

### Performance Features
- Code splitting for faster loading
- Lazy loading of components
- Optimized chart rendering
- Responsive image loading

## Future Enhancements

### Planned Features
- **Real-time WebSocket integration**
- **Voice command interface**
- **Multi-language support**
- **Historical race data analysis**
- **Team radio integration**
- **Live video feeds**

### Technical Improvements
- **PWA capabilities**
- **Offline mode**
- **Advanced caching**
- **Performance monitoring**

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.

---

**Built for Ferrari F1 Team** - Professional racing strategy dashboard designed for real-time race operations. 