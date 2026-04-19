import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Color, Vector3 } from 'three';

const ACT_CAMERA = {
  1: { position: new Vector3(0, 2.6, 6), target: new Vector3(0, 1.1, 0) },
  2: { position: new Vector3(0, 4.5, 10), target: new Vector3(0, 1.2, -8) },
  3: { position: new Vector3(0, 18, 26), target: new Vector3(0, 0, 0) },
  4: { position: new Vector3(0, 6.5, 14), target: new Vector3(0, 1.4, -2) },
  5: { position: new Vector3(0, 7.5, 12), target: new Vector3(0, 2.2, -1) },
};

export default function StableStoryScene({ act = 1, progress = 0 }) {
  const targetRef = useRef(new Vector3());

  useFrame((state) => {
    const config = ACT_CAMERA[act] || ACT_CAMERA[1];
    state.camera.position.lerp(config.position, 0.08);
    targetRef.current.lerp(config.target, 0.12);
    state.camera.lookAt(targetRef.current);
  });

  return (
    <>
      <color attach="background" args={['#09101c']} />
      <fog attach="fog" args={['#101829', 12, 48]} />
      <ambientLight intensity={0.95} color="#ccd8ff" />
      <directionalLight position={[7, 10, 6]} intensity={1.4} color="#ffe0b0" />
      <pointLight position={[-5, 4, 5]} intensity={12} distance={24} color="#304d9a" />

      {act === 1 && <FamilyAct progress={progress} />}
      {act === 2 && <CorridorAct progress={progress} />}
      {act === 3 && <NationAct progress={progress} />}
      {act === 4 && <InterventionAct progress={progress} />}
      {act === 5 && <DashboardAct progress={progress} />}

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <planeGeometry args={[120, 120]} />
        <meshStandardMaterial color="#0b1320" />
      </mesh>
    </>
  );
}

function FamilyAct({ progress }) {
  return (
    <group>
      <mesh position={[-2.6, 1, -1]} castShadow>
        <boxGeometry args={[3.4, 2, 2.8]} />
        <meshStandardMaterial color="#8a562a" />
      </mesh>
      <mesh position={[-2.6, 2.4, -1]} rotation={[0, Math.PI / 4, 0]}>
        <coneGeometry args={[2.8, 1.3, 4]} />
        <meshStandardMaterial color="#693b18" />
      </mesh>
      <Person position={[0, 0, 0]} scale={1.15} body="#f5b042" skirt="#6f4420" />
      <Person
        position={[0.8, 0, 0.5]}
        scale={0.72}
        body="#c6553a"
        skirt="#c6553a"
        glow={Math.max(0, (progress - 0.35) * 1.8)}
      />
    </group>
  );
}

function CorridorAct({ progress }) {
  const count = 48;
  return (
    <group position={[0, 0, 12]}>
      {[-18, -6, 6, 18].map((z) => (
        <mesh key={z} position={[0, 2.8, z]}>
          <torusGeometry args={[6.5, 0.18, 12, 36]} />
          <meshStandardMaterial color="#f5b042" emissive="#f5b042" emissiveIntensity={0.55} />
        </mesh>
      ))}
      {Array.from({ length: count }).map((_, i) => {
        const lane = (i % 8) - 3.5;
        const depth = -Math.floor(i / 8) * 2.2;
        const dropped = i / count > 1 - progress * 0.75;
        return (
          <mesh key={`corr-${i}`} position={[lane * 1.1, dropped ? -0.8 : 0.35, depth]}>
            <sphereGeometry args={[0.18, 14, 14]} />
            <meshStandardMaterial
              color={dropped ? '#4f5f7d' : '#f4f0e6'}
              emissive={dropped ? '#101829' : '#b48534'}
              emissiveIntensity={dropped ? 0.04 : 0.1}
            />
          </mesh>
        );
      })}
    </group>
  );
}

function NationAct() {
  return (
    <group>
      {Array.from({ length: 36 }).map((_, i) => (
        <mesh key={`grid-${i}`} position={[((i % 6) - 2.5) * 6, 0.25, -Math.floor(i / 6) * 6 + 12]}>
          <boxGeometry args={[0.14, 0.14, 24]} />
          <meshStandardMaterial color="#f5b042" emissive="#f5b042" emissiveIntensity={0.28} />
        </mesh>
      ))}
      {Array.from({ length: 60 }).map((_, i) => (
        <mesh key={`pulse-${i}`} position={[((i % 10) - 4.5) * 3.2, 0.8 + (i % 4) * 0.35, -Math.floor(i / 10) * 4.2 + 8]}>
          <sphereGeometry args={[0.12, 10, 10]} />
          <meshStandardMaterial color="#8fb6ff" emissive="#5378df" emissiveIntensity={0.55} />
        </mesh>
      ))}
    </group>
  );
}

function InterventionAct({ progress }) {
  const activeHeight = 0.8 + progress * 1.1;
  const columns = [
    { color: '#f5b042', x: -5, z: 2 },
    { color: '#47b7a0', x: -1.5, z: -1.5 },
    { color: '#5a7bff', x: 2, z: -5 },
    { color: '#c6553a', x: 5.5, z: -8.5 },
  ];

  return (
    <group>
      {columns.map((column, index) => (
        <group key={column.color} position={[column.x, 0, column.z]}>
          <mesh position={[0, activeHeight / 2, 0]}>
            <cylinderGeometry args={[0.5, 0.5, activeHeight + index * 0.2, 24]} />
            <meshStandardMaterial color={column.color} emissive={column.color} emissiveIntensity={0.7} />
          </mesh>
          <mesh position={[0, activeHeight + 0.2, 0]}>
            <torusGeometry args={[0.9, 0.08, 16, 40]} />
            <meshStandardMaterial color={column.color} emissive={column.color} emissiveIntensity={0.9} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function DashboardAct({ progress }) {
  const barColor = new Color('#f5b042');
  return (
    <group position={[0, 0.5, -2]}>
      <mesh position={[0, 1.8, 0]}>
        <boxGeometry args={[10, 5.4, 0.2]} />
        <meshStandardMaterial color="#141e31" />
      </mesh>
      {Array.from({ length: 8 }).map((_, i) => {
        const height = 0.8 + ((i % 4) + progress) * 0.6;
        return (
          <mesh key={`bar-${i}`} position={[-3.5 + i, height / 2 + 0.5, 0.2]}>
            <boxGeometry args={[0.55, height, 0.2]} />
            <meshStandardMaterial color={barColor} emissive={barColor} emissiveIntensity={0.25} />
          </mesh>
        );
      })}
      <mesh position={[-2.4, 2.5, 0.22]}>
        <boxGeometry args={[2.2, 1.3, 0.12]} />
        <meshStandardMaterial color="#21314b" />
      </mesh>
      <mesh position={[2.2, 2.2, 0.22]}>
        <boxGeometry args={[3.4, 2, 0.12]} />
        <meshStandardMaterial color="#1d2940" />
      </mesh>
    </group>
  );
}

function Person({ position, scale = 1, body, skirt, glow = 0 }) {
  return (
    <group position={position} scale={scale}>
      <mesh position={[0, 1.7, 0]}>
        <sphereGeometry args={[0.18, 12, 12]} />
        <meshStandardMaterial color="#a66a2c" />
      </mesh>
      <mesh position={[0, 1.1, 0]}>
        <capsuleGeometry args={[0.22, 0.9, 4, 8]} />
        <meshStandardMaterial color={body} emissive={glow > 0 ? '#f5b042' : '#000000'} emissiveIntensity={glow} />
      </mesh>
      <mesh position={[0, 0.32, 0]}>
        <coneGeometry args={[0.35, 0.7, 6]} />
        <meshStandardMaterial color={skirt} />
      </mesh>
    </group>
  );
}
