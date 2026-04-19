import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Color, Vector3 } from 'three';
import { useScenarioStore } from '../state/scenario.js';

const CAMERA_MODES = {
  orbit: {
    position: new Vector3(0, 7, 15),
    target: new Vector3(0, 1.6, -1),
  },
  flythrough: {
    position: new Vector3(0, 2.5, 8.5),
    target: new Vector3(0, 1.3, -9),
  },
  top: {
    position: new Vector3(0, 24, 0.01),
    target: new Vector3(0, 0, -3),
  },
};

const CHAPTER_STATES = {
  home: {
    motherX: -2.6,
    childX: -1.8,
    corridorGlow: 0.08,
    rescueGlow: 0.15,
    dropoutOffset: 0,
  },
  reminder: {
    motherX: -0.9,
    childX: -0.2,
    corridorGlow: 0.18,
    rescueGlow: 0.48,
    dropoutOffset: 0,
  },
  corridor: {
    motherX: 1.2,
    childX: 2.1,
    corridorGlow: 0.36,
    rescueGlow: 0.22,
    dropoutOffset: -1.2,
  },
  rescue: {
    motherX: 3.6,
    childX: 4.4,
    corridorGlow: 0.22,
    rescueGlow: 0.82,
    dropoutOffset: 0.6,
  },
};

export default function StableSimulationScene({ cameraMode = 'orbit', scale = 'community', chapter = 'home' }) {
  const interventions = useScenarioStore((s) => s.interventions);
  const cameraTargetRef = useRef(new Vector3());
  const state = CHAPTER_STATES[chapter] || CHAPTER_STATES.home;

  const cohort = useMemo(() => {
    const scaleMultiplier = {
      family: 8,
      community: 24,
      state: 40,
      nation: 56,
    }[scale] || 24;

    return Array.from({ length: scaleMultiplier }, (_, index) => ({
      id: `agent-${scale}-${index}`,
      x: ((index % 10) - 4.5) * 1.1,
      z: -Math.floor(index / 10) * 1.5 - 2.5,
      size: 0.13 + (index % 4) * 0.02,
    }));
  }, [scale]);

  useFrame((frameState) => {
    const config = CAMERA_MODES[cameraMode] || CAMERA_MODES.orbit;
    frameState.camera.position.lerp(config.position, 0.08);
    cameraTargetRef.current.lerp(config.target, 0.12);
    frameState.camera.lookAt(cameraTargetRef.current);
  });

  return (
    <>
      <color attach="background" args={['#0b1020']} />
      <fog attach="fog" args={['#101829', 12, 36]} />
      <ambientLight intensity={0.92} color="#c7d5ff" />
      <directionalLight position={[6, 10, 5]} intensity={1.4} color="#ffe6ba" />
      <pointLight position={[-6, 4, 6]} intensity={10} distance={20} color="#3559a8" />

      <HomeCluster chapter={chapter} />
      <Corridor chapter={chapter} glow={state.corridorGlow} />
      <ClinicNodes interventions={interventions} rescueGlow={state.rescueGlow} />
      <FamilyJourney chapter={chapter} motherX={state.motherX} childX={state.childX} dropoutOffset={state.dropoutOffset} />
      <CommunityCohort cohort={cohort} chapter={chapter} />

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, -1]}>
        <planeGeometry args={[44, 44]} />
        <meshStandardMaterial color="#09111d" />
      </mesh>
    </>
  );
}

function HomeCluster({ chapter }) {
  const homeGlow = chapter === 'home' ? 0.55 : 0.18;
  return (
    <group position={[-5.4, 0, 2]}>
      <mesh position={[0, 1.05, 0]}>
        <boxGeometry args={[3.8, 2.1, 3]} />
        <meshStandardMaterial color="#8b572d" emissive="#60381a" emissiveIntensity={0.14} />
      </mesh>
      <mesh position={[0, 2.45, 0]} rotation={[0, Math.PI / 4, 0]}>
        <coneGeometry args={[3, 1.4, 4]} />
        <meshStandardMaterial color="#6d3f1b" />
      </mesh>
      <mesh position={[0.8, 1, 1.56]}>
        <boxGeometry args={[0.65, 1, 0.08]} />
        <meshStandardMaterial color="#f5b042" emissive="#f5b042" emissiveIntensity={homeGlow} />
      </mesh>
    </group>
  );
}

function Corridor({ chapter, glow }) {
  const rings = [-3, -8, -13];
  return (
    <group>
      {rings.map((z, index) => (
        <mesh key={z} position={[0, 2.8, z]}>
          <torusGeometry args={[6.3, 0.16, 16, 40]} />
          <meshStandardMaterial
            color={chapter === 'corridor' && index === 1 ? '#c6553a' : '#f5b042'}
            emissive={chapter === 'corridor' && index === 1 ? '#c6553a' : '#f5b042'}
            emissiveIntensity={glow + index * 0.05}
          />
        </mesh>
      ))}
      <mesh position={[0, 0.05, -8]}>
        <boxGeometry args={[15, 0.08, 18]} />
        <meshStandardMaterial color="#142237" />
      </mesh>
    </group>
  );
}

function ClinicNodes({ interventions, rescueGlow }) {
  const meta = [
    { key: 'a1', x: -6.5, z: -11.5, color: '#f5b042' },
    { key: 'a2', x: -2.1, z: -11.5, color: '#47b7a0' },
    { key: 'a3', x: 2.2, z: -11.5, color: '#5a7bff' },
    { key: 'a4', x: 6.5, z: -11.5, color: '#c6553a' },
  ];

  return (
    <group>
      {meta.map((item) => (
        <InterventionBeacon
          key={item.key}
          active={!!interventions[item.key]}
          color={item.color}
          position={[item.x, 0, item.z]}
          rescueGlow={rescueGlow}
        />
      ))}
    </group>
  );
}

function FamilyJourney({ chapter, motherX, childX, dropoutOffset }) {
  const emphasis = chapter === 'rescue' ? 0.55 : chapter === 'corridor' ? 0.18 : 0.28;
  return (
    <group>
      <Person position={[motherX, 0, 0.8]} scale={1.12} body="#f5b042" skirt="#72461f" glow={emphasis} />
      <Person position={[childX, Math.max(dropoutOffset, 0), 1.35]} scale={0.72} body="#c6553a" skirt="#c6553a" glow={chapter === 'corridor' ? 0.1 : 0.5} />
      {chapter === 'corridor' && (
        <mesh position={[childX, -0.35, 1.35]}>
          <circleGeometry args={[0.8, 30]} />
          <meshStandardMaterial color="#c6553a" transparent opacity={0.18} />
        </mesh>
      )}
      {chapter === 'rescue' && (
        <mesh position={[childX + 0.2, 2.1, 1.15]}>
          <torusGeometry args={[0.9, 0.08, 16, 40]} />
          <meshStandardMaterial color="#47b7a0" emissive="#47b7a0" emissiveIntensity={0.9} />
        </mesh>
      )}
    </group>
  );
}

function CommunityCohort({ cohort, chapter }) {
  const muted = chapter === 'home';
  return (
    <group>
      {cohort.map((child) => (
        <mesh key={child.id} position={[child.x, 0.24, child.z]}>
          <sphereGeometry args={[child.size, 14, 14]} />
          <meshStandardMaterial
            color={muted ? '#c6cfdf' : '#f1ede0'}
            emissive={chapter === 'rescue' ? '#7fb4ff' : '#6b5429'}
            emissiveIntensity={chapter === 'rescue' ? 0.12 : 0.04}
          />
        </mesh>
      ))}
    </group>
  );
}

function InterventionBeacon({ active, color, position, rescueGlow }) {
  const groupRef = useRef(null);
  const ringColor = useMemo(() => new Color(color), [color]);

  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime;
    groupRef.current.position.y = 0.9 + Math.sin(t * 1.7 + position[0]) * 0.08;
    groupRef.current.rotation.y += active ? 0.018 : 0.008;
  });

  return (
    <group ref={groupRef} position={position}>
      <mesh>
        <cylinderGeometry args={[0.42, 0.42, active ? 1.8 : 1.0, 20]} />
        <meshStandardMaterial
          color={active ? color : '#344155'}
          emissive={active ? color : '#141c2a'}
          emissiveIntensity={active ? rescueGlow : 0.08}
        />
      </mesh>
      <mesh position={[0, active ? 1.05 : 0.65, 0]}>
        <torusGeometry args={[0.85, 0.07, 16, 36]} />
        <meshStandardMaterial color={ringColor} emissive={ringColor} emissiveIntensity={active ? rescueGlow + 0.1 : 0.12} />
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
