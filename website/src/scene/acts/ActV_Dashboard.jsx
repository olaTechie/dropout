import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';

export default function ActV_Dashboard() {
  const meshRef = useRef();
  useFrame(() => {
    if (meshRef.current) meshRef.current.rotation.y += 0.0005;
  });

  return (
    <>
      <fog attach="fog" args={['#05070C', 20, 100]} />
      <group ref={meshRef}>
        {Array.from({ length: 200 }).map((_, i) => (
          <mesh key={i} position={[(Math.random() - 0.5) * 80, (Math.random()) * 20, (Math.random() - 0.5) * 80]}>
            <sphereGeometry args={[0.05, 4, 4]} />
            <meshBasicMaterial color="#F5B042" />
          </mesh>
        ))}
      </group>
    </>
  );
}
