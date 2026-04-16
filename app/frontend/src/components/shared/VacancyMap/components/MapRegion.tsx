import type { RegionData } from '../data/svgMapData';

interface MapRegionProps {
    region: RegionData;
    onMouseEnter: (region: RegionData) => void;
    onMouseLeave: () => void;
}

export default function MapRegion({ region, onMouseEnter, onMouseLeave }: MapRegionProps) {
    return (
        <g key={region.id} className="region">
            <path
                d={region.path}
                onMouseEnter={() => onMouseEnter(region)}
                onMouseLeave={onMouseLeave}
            />
        </g>
    );
}
