import { useEffect, useState } from 'react';
import { useLoader } from '@react-three/fiber';
import { TextureLoader } from 'three';
import { feature } from 'topojson-client';
import { geoPath, geoMercator } from 'd3-geo';
import { loadData } from '../../lib/dataLoader.js';

export default function NigeriaMap() {
  const [geoJson, setGeoJson] = useState(null);
  const [cascade, setCascade] = useState(null);

  useEffect(() => {
    loadData('nigeria_zones').then((topo) => setGeoJson(feature(topo, topo.objects.states)));
    loadData('cascade').then(setCascade);
  }, []);

  if (!geoJson) return null;

  // Simple stand-in: colored extruded plane per state
  return (
    <group position={[0, 0, 0]} scale={0.08}>
      {geoJson.features.map((f, i) => (
        <mesh key={i} position={[0, 0, 0]}>
          <boxGeometry args={[2, 0.3 + (i % 10) * 0.1, 2]} />
          <meshStandardMaterial color="#C6553A" emissive="#C6553A" emissiveIntensity={0.2} />
        </mesh>
      ))}
    </group>
  );
}
