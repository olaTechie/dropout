import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

export default function ActIII_Nation({ progress = 0 }) {
  const groupRef = useRef();
  useFrame(() => {
    if (groupRef.current) groupRef.current.rotation.y += 0.002;
  });

  return (
    <group ref={groupRef}>
      <fog attach="fog" args={['#05070C', 30, 200]} />

      {/* Lattice of light — many parallel corridors */}
      {Array.from({ length: 50 }).map((_, i) => (
        <mesh key={i} position={[(i - 25) * 3, 0, 0]}>
          <boxGeometry args={[0.1, 0.05, 60]} />
          <meshStandardMaterial
            color="#F5B042"
            emissive="#F5B042"
            emissiveIntensity={0.3 + Math.random() * 0.3}
            transparent
            opacity={0.7}
          />
        </mesh>
      ))}

      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[200, 200]} />
        <meshStandardMaterial color="#05070C" />
      </mesh>
    </group>
  );
}
