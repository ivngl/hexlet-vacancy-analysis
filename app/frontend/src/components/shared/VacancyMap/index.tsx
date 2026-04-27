import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import './Map.css';

import { Tooltip } from '@mantine/core';
import MapPointer from './components/MapPointer';
import MapRegion from './components/MapRegion';
import { ZoomControls } from './components/ZoomControls';
import { MOCK_REGIONS, type RegionData } from './data/svgMapData';
import calculatePointerData from './utils/calculatePointerData';
import type { FetchVacancyConfig } from './utils/fetchVacancies';
import fetchVacancies from './utils/fetchVacancies';



const MAP_WIDTH = 1280;
const MAP_HEIGHT = 760;
const INITIAL_VIEW_BOX = { x: 0, y: 0, width: 1220, height: 860 };
const SCALE_FACTOR = 0.1;
const MIN_SCALE = 0.1;
const MAX_SCALE = 1;
const CHUNK_SIZE = 100;

// API constants
const SUPERJOB_API_URL = 'https://api.superjob.ru/2.0/vacancies';
const HH_API_URL = 'https://api.hh.ru/vacancies';
const SUPERJOB_VACANCY_CATEGORY = '33';
const HH_PROFESSIONAL_ROLE = '96';
const VACANCIES_PER_PAGE = '1';


interface TooltipPosition {
  x: number;
  y: number;
}



export default function VacancyMap() {
  const [regions, setRegions] = useState<RegionData[]>(() =>
    MOCK_REGIONS.map((r) => ({ ...r, pointer: null })),
  );
  const [hoveredRegion, setHoveredRegion] = useState<RegionData | null>(
    null,
  );
  const [mousePos, setMousePos] = useState<TooltipPosition>({ x: 0, y: 0 });
  const [scale, setScale] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const svgRef = useRef<SVGSVGElement | null>(null);

  // Загрузка данных о вакансиях
  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    async function loadVacancies() {
      setIsLoading(true);
      setError(null);

      try {
        const updatedRegions: RegionData[] = [];

        for (let i = 0; i < regions.length; i += CHUNK_SIZE) {
          const chunk = regions.slice(i, i + CHUNK_SIZE);

          const chunkPromises = chunk.map((region) => {
            const SUPERJOB_CONFIG: FetchVacancyConfig = {
              baseUrl: SUPERJOB_API_URL,
              params: {
                town: region.name,
                count: VACANCIES_PER_PAGE,
                page: '1',
                catalogues: SUPERJOB_VACANCY_CATEGORY,
              },
              headers: { 'X-Api-App-Id': import.meta.env.SUPERJOB_API_KEY },
              parseResponse: (data: Record<string, number>) => data.total ?? 0,
            };

            const HH_CONFIG: FetchVacancyConfig = {
              baseUrl: HH_API_URL,
              params: {
                area: String(region.hh_area_id),
                per_page: VACANCIES_PER_PAGE,
                page: '1',
                professional_role: HH_PROFESSIONAL_ROLE,
              },
              parseResponse: (data: Record<string, number>) => data.found ?? 0,
            };
            return fetchVacancies(region.name, [SUPERJOB_CONFIG, HH_CONFIG], signal).then((totalVacancies) => {

              const updated: RegionData = {
                ...region,
                totalVacancies,
                pointer: totalVacancies ? calculatePointerData({ ...region, totalVacancies }, scale) : null,
              };
              return updated;
            })
          }
          );

          const chunkResults = await Promise.all(chunkPromises);
          updatedRegions.push(...chunkResults);
        }

        setRegions(updatedRegions);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        if (signal.aborted) return;
        setError(message);
        console.error('Failed to load vacancies:', err);
      } finally {
        if (!signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadVacancies();

    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Обработчики мыши
  const handleMouseEnter = useCallback((region: RegionData) => {
    setHoveredRegion(region);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setHoveredRegion(null);
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    setMousePos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  }, []);

  // Zoom контролы
  const handleZoomIn = useCallback(() => {
    setScale((prev) => Math.max(MIN_SCALE, prev - SCALE_FACTOR));
  }, []);

  const handleZoomOut = useCallback(() => {
    setScale((prev) => Math.min(MAX_SCALE, prev + SCALE_FACTOR));
  }, []);

  const regionsWithPointers = useMemo(() => {
    const mapRegions: React.ReactNode[] = [];
    const mapPointers: React.ReactNode[] = [];

    for (const region of regions) {
      const pointer = region.totalVacancies ? calculatePointerData(region, scale) : null;
      const regionWithPointer: RegionData = { ...region, pointer };

      mapRegions.push(
        <MapRegion
          key={region.id}
          region={regionWithPointer}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        />,
      );

      if (pointer) {
        mapPointers.push(
          <MapPointer
            key={`${region.id}-pointer`}
            region={regionWithPointer}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
          />,
        );
      }
    }

    return [...mapRegions, ...mapPointers];
  }, [regions, scale, handleMouseEnter, handleMouseLeave]);

  return (
    <div className="map-container">
      {isLoading && <div className="map-loading">Загрузка данных...</div>}
      {error && <div className="map-error">{error}</div>}

      <svg
        ref={svgRef}
        className="map-svg"
        width={MAP_WIDTH / scale}
        height={MAP_HEIGHT / scale}
        viewBox={`${INITIAL_VIEW_BOX.x} ${INITIAL_VIEW_BOX.y} ${INITIAL_VIEW_BOX.width} ${INITIAL_VIEW_BOX.height}`}
        onMouseMove={handleMouseMove}
      >
        {regionsWithPointers}

        {hoveredRegion && (
          <>
            <MapRegion
              key={`${hoveredRegion.id}-hovered`}
              region={hoveredRegion}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            />
            <MapPointer
              key={`${hoveredRegion.id}-hovered-pointer`}
              region={hoveredRegion}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            />
          </>
        )}
      </svg>

      <ZoomControls
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        canZoomOut={scale < MAX_SCALE}
        canZoomIn={scale > MIN_SCALE}
      />

      {hoveredRegion && (
        <Tooltip
          position="top"
          opened
          label={hoveredRegion.name}
          offset={{ mainAxis: 40, crossAxis: 70 }}
        >
          <div
            className='map-tooltip'
            style={{
              left: mousePos.x,
              top: mousePos.y,
            }}
          >
          </div>
        </Tooltip>
      )}
    </div>
  );
}
