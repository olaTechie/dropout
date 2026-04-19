import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import Cohort from '../props/Cohort.jsx';

export default function ActII_Corridor({ progress = 0 }) {
  const gateRef = useRef();
  useFrame((state) => {
    if (gateRef.current) gateRef.current.rotation.y += 0.005;
  });

  return (
    <>
      <fog attach="fog" args={['#0D1220', 10, 80]} />

      {/* Translucent floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
        <planeGeometry args={[60, 200]} />
        <meshStandardMaterial color="#1A2340" transparent opacity={0.5} />
      </mesh>

      {/* Gates at 6w, 10w, 14w */}
      {[-30, -10, 10, 30].map((z, i) => (
        <mesh key={z} position={[0, 3, z]} ref={i === 1 ? gateRef : null}>
          <torusGeometry args={[8, 0.2, 8, 32]} />
          <meshStandardMaterial color="#F5B042" emissive="#F5B042" emissiveIntensity={0.4} />
        </mesh>
      ))}

      <Cohort count={1000} progress={progress} spread={12} />
    </>
  );
}
