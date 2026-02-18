import React, { useState } from 'react';
import type { MouseEvent } from 'react'
import './RussiaMap.css';

// Type definitions
interface City {
  id: number;
  name: string;
  x: number;
  y: number;
  population: string;
  area: string;
  founded: string;
  description: string;
  temperature: string;
  timezone: string;
}

interface MousePos {
  x: number;
  y: number;
}

// Union type for event handling (SVG event or custom object from sidebar)
type MouseEnterEvent = MouseEvent<HTMLElement> | { clientX: number; clientY: number };

export const RussiaMap: React.FC = () => {
  const [hoveredCity, setHoveredCity] = useState<City | null>(null);
  const [mousePos, setMousePos] = useState<MousePos>({ x: 0, y: 0 });

  // Major Russian cities with coordinates (approximate positions on SVG)
  const cities: City[] = [
    {
      id: 1,
      name: 'Moscow',
      x: 280,
      y: 220,
      population: '12.6 million',
      area: '2,511 km²',
      founded: '1147',
      description: 'Capital and largest city of Russia, major political, economic, and cultural center.',
      temperature: '5.8°C',
      timezone: 'MSK (UTC+3)'
    },
    {
      id: 2,
      name: 'Saint Petersburg',
      x: 260,
      y: 160,
      population: '5.4 million',
      area: '1,439 km²',      founded: '1703',
      description: 'Former capital, cultural capital, known for its imperial architecture and White Nights.',
      temperature: '5.0°C',
      timezone: 'MSK (UTC+3)'
    },
    {
      id: 3,
      name: 'Novosibirsk',
      x: 520,
      y: 240,
      population: '1.6 million',
      area: '505 km²',
      founded: '1893',
      description: 'Third most populous city in Russia, major industrial and scientific center of Siberia.',
      temperature: '1.0°C',
      timezone: 'NOVT (UTC+7)'
    },
    {
      id: 4,
      name: 'Yekaterinburg',
      x: 420,
      y: 210,
      population: '1.5 million',
      area: '495 km²',
      founded: '1723',
      description: 'Major industrial city on the border of Europe and Asia, former residence of the Romanovs.',
      temperature: '2.5°C',
      timezone: 'YEKT (UTC+5)'
    },
    {
      id: 5,
      name: 'Kazan',
      x: 340,
      y: 230,
      population: '1.3 million',
      area: '425 km²',
      founded: '1005',
      description: 'Capital of Tatarstan, major cultural and sporting center, known for its Kremlin.',
      temperature: '4.5°C',
      timezone: 'MSK (UTC+3)'
    },
    {
      id: 6,
      name: 'Nizhny Novgorod',
      x: 300,
      y: 230,
      population: '1.2 million',
      area: '410 km²',
      founded: '1221',
      description: 'Fifth largest city, major economic and cultural center on the Volga River.',      temperature: '4.2°C',
      timezone: 'MSK (UTC+3)'
    },
    {
      id: 7,
      name: 'Vladivostok',
      x: 880,
      y: 320,
      population: '606,000',
      area: '331 km²',
      founded: '1860',
      description: 'Major Pacific port city, terminus of the Trans-Siberian Railway.',
      temperature: '5.5°C',
      timezone: 'VLAT (UTC+10)'
    },
    {
      id: 8,
      name: 'Sochi',
      x: 320,
      y: 340,
      population: '443,000',
      area: '3,502 km²',
      founded: '1838',
      description: 'Resort city on the Black Sea, host of the 2014 Winter Olympics.',
      temperature: '14.2°C',
      timezone: 'MSK (UTC+3)'
    },
    {
      id: 9,
      name: 'Kaliningrad',
      x: 140,
      y: 190,
      population: '489,000',
      area: '224 km²',
      founded: '1255',
      description: 'Westernmost major city, Russian exclave between Poland and Lithuania.',
      temperature: '7.8°C',
      timezone: 'EET (UTC+2)'
    },
    {
      id: 10,
      name: 'Krasnoyarsk',
      x: 620,
      y: 250,
      population: '1.1 million',
      area: '354 km²',
      founded: '1628',
      description: 'One of the largest cities in Siberia, major industrial and educational center.',
      temperature: '-0.7°C',
      timezone: 'KRAT (UTC+7)'    }
  ];

  const handleMouseEnter = (city: City, event: MouseEnterEvent) => {
    setHoveredCity(city);
    setMousePos({ x: event.clientX, y: event.clientY });
  };

  const handleMouseMove = (event: MouseEvent<SVGSVGElement>) => {
    if (hoveredCity) {
      setMousePos({ x: event.clientX, y: event.clientY });
    }
  };

  const handleMouseLeave = () => {
    setHoveredCity(null);
  };

  return (
    <div className="map-container">
      <h2>Interactive Map of Russia</h2>
      <p>Hover over city markers to view detailed information</p>
      
      <div className="map-wrapper">
        <svg 
          viewBox="0 0 1000 500" 
          className="russia-svg"
          onMouseMove={handleMouseMove}
        >
          {/* Simplified Russia map outline */}
          <defs>
            <linearGradient id="landGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4a7c59" />
              <stop offset="100%" stopColor="#3d6b4f" />
            </linearGradient>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="2" dy="2" stdDeviation="2" floodOpacity="0.3" />
            </filter>
          </defs>

          {/* Russia outline - simplified path */}
          <path
            d="M 50,150 Q 100,100 200,80 L 300,60 L 400,70 L 500,60 L 600,80 L 700,70 L 800,90 L 900,100 
               L 950,150 L 920,200 L 900,250 L 850,280 L 800,300 L 750,280 L 700,300 L 650,280 L 600,300 
               L 550,280 L 500,300 L 450,280 L 400,300 L 350,280 L 300,300 L 250,280 L 200,300 L 150,280 
               L 100,250 L 80,200 Z"
            fill="url(#landGradient)"
            stroke="#2d4a3e"
            strokeWidth="2"
            filter="url(#shadow)"            className="russia-outline"
          />

          {/* Ural Mountains indicator */}
          <path
            d="M 420,100 Q 430,150 420,200 Q 410,250 420,300"
            fill="none"
            stroke="#8b7355"
            strokeWidth="3"
            strokeDasharray="5,5"
            opacity="0.6"
          />
          <text x="430" y="200" className="mountain-label" fill="#8b7355" fontSize="12">
            Ural Mountains
          </text>

          {/* Major rivers */}
          <path
            d="M 280,180 Q 290,220 280,280 Q 270,320 260,350"
            fill="none"
            stroke="#4a90e2"
            strokeWidth="2"
            opacity="0.5"
          />
          <text x="265" y="280" className="river-label" fill="#4a90e2" fontSize="10">
            Volga
          </text>

          {/* City markers */}
          {cities.map((city) => (
            <g key={city.id} className="city-group">
              {/* Pulse animation circle */}
              <circle
                cx={city.x}
                cy={city.y}
                r="8"
                fill="rgba(231, 76, 60, 0.3)"
                className="pulse-circle"
              />
              
              {/* Main marker circle */}
              <circle
                cx={city.x}
                cy={city.y}
                r="6"
                fill="#e74c3c"
                stroke="#fff"
                strokeWidth="2"
                className="city-marker"
                onMouseEnter={(e) => handleMouseEnter(city, e)}                onMouseLeave={handleMouseLeave}
                style={{ cursor: 'pointer' }}
              />
              
              {/* City name label */}
              <text
                x={city.x}
                y={city.y - 12}
                textAnchor="middle"
                className="city-label"
                fill="#2c3e50"
                fontSize="11"
                fontWeight="600"
              >
                {city.name}
              </text>
            </g>
          ))}

          {/* Scale indicator */}
          <g transform="translate(50, 450)">
            <line x1="0" y1="0" x2="100" y2="0" stroke="#2c3e50" strokeWidth="2" />
            <line x1="0" y1="-5" x2="0" y2="5" stroke="#2c3e50" strokeWidth="2" />
            <line x1="100" y1="-5" x2="100" y2="5" stroke="#2c3e50" strokeWidth="2" />
            <text x="50" y="20" textAnchor="middle" fill="#2c3e50" fontSize="12">
              1000 km
            </text>
          </g>
        </svg>

        {/* Tooltip */}
        {hoveredCity && (
          <div 
            className="city-tooltip"
            style={{ 
              top: mousePos.y - 350, 
              left: mousePos.x - 400 
            } as React.CSSProperties}
          >
            <div className="tooltip-header">
              <h3>{hoveredCity.name}</h3>
              <div className="tooltip-close" onClick={handleMouseLeave}>×</div>
            </div>
          
            <div className="tooltip-content">
              <p className="tooltip-description">{hoveredCity.description}</p>
            
              <div className="tooltip-grid">
                <div className="tooltip-item">
                  <span className="tooltip-label">Population: </span>                  <span className="tooltip-value">{hoveredCity.population}</span>
                </div>
                <div className="tooltip-item">
                  <span className="tooltip-label">Area: </span>
                  <span className="tooltip-value">{hoveredCity.area}</span>
                </div>
                <div className="tooltip-item">
                  <span className="tooltip-label">Founded: </span>
                  <span className="tooltip-value">{hoveredCity.founded}</span>
                </div>
                <div className="tooltip-item">
                  <span className="tooltip-label">Temperature: </span>
                  <span className="tooltip-value">{hoveredCity.temperature}</span>
                </div>
                <div className="tooltip-item">
                  <span className="tooltip-label">Timezone: </span>
                  <span className="tooltip-value">{hoveredCity.timezone}</span>
                </div>
              </div>
            </div>
          
            <div className="tooltip-arrow"></div>
          </div>
        )}
      </div>

      {/* City list sidebar */}
      <div className="city-list">
        <h3>Major Cities</h3>
        <ul>
          {cities.map((city) => (
            <li 
              key={city.id}
              className={`city-list-item ${hoveredCity?.id === city.id ? 'active' : ''}`}
              onMouseEnter={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                handleMouseEnter(city, { clientX: rect.left + 50, clientY: rect.top });
              }}
              onMouseLeave={handleMouseLeave}
            >
              <div className="city-dot"></div>
              <div className="city-info">
                <span className="city-name">{city.name}</span>
                <span className="city-pop">{city.population}</span>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>  );
};
