import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

export default function InterventionEffect({ type, active, position = [0, 0, 0] }) {
  const ringRef = useRef();
  useFrame((state) => {
    if (!ringRef.current || !active) return;
    const t = state.clock.elapsedTime;
    ringRef.current.scale.setScalar(1 + Math.sin(t * 2) * 0.1);
  });

  if (!active) return null;

  const colors = {
    a1: '#F5B042', // SMS — saffron
    a2: '#47B7A0', // CHW — verdigris
    a3: '#5A7BFF', // Recall — iris
    a4: '#C6553A', // Incentive — terracotta
  };

  return (
    <mesh ref={ringRef} position={position}>
      <torusGeometry args={[2, 0.1, 8, 24]} />
      <meshStandardMaterial color={colors[type]} emissive={colors[type]} emissiveIntensity={0.8} transparent opacity={0.6} />
    </mesh>
  );
}
