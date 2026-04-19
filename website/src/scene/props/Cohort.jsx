import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Matrix4, Object3D } from 'three';

const tempObj = new Object3D();

export default function Cohort({ count = 1000, progress = 0, spread = 40 }) {
  const meshRef = useRef();

  const seeds = useMemo(() => {
    const s = [];
    for (let i = 0; i < count; i++) {
      s.push({
        x: (Math.random() - 0.5) * spread,
        z: (Math.random() - 0.5) * spread * 2,
        y: 0,
        dropStart: 0.2 + Math.random() * 0.6,
        dropRate: 0.05 + Math.random() * 0.1,
      });
    }
    return s;
  }, [count, spread]);

  useFrame(() => {
    if (!meshRef.current) return;
    for (let i = 0; i < seeds.length; i++) {
      const s = seeds[i];
      const dropping = progress > s.dropStart && (i / count) > progress;
      const yOffset = dropping ? -((progress - s.dropStart) * 10) : 0;
      tempObj.position.set(s.x, Math.max(s.y + yOffset, -5), s.z);
      tempObj.scale.setScalar(yOffset < -3 ? 0.01 : 0.3);
      tempObj.updateMatrix();
      meshRef.current.setMatrixAt(i, tempObj.matrix);
    }
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]} castShadow>
      <sphereGeometry args={[0.15, 8, 8]} />
      <meshStandardMaterial color="#F5B042" />
    </instancedMesh>
  );
}
