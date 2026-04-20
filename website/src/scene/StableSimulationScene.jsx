import { forwardRef, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { CatmullRomCurve3, Color, TubeGeometry, Vector3 } from 'three';
import { useScenarioStore } from '../state/scenario.js';

const CAMERA_MODES = {
  orbit: {
    position: new Vector3(0, 9, 18),
    target: new Vector3(0, 1.8, -2),
  },
  flythrough: {
    position: new Vector3(0, 3.5, 10),
    target: new Vector3(0, 1.4, -8),
  },
  top: {
    position: new Vector3(0, 26, 0.01),
    target: new Vector3(0, 0, -5),
  },
};

const CHAPTER_STATES = {
  home: {
    heroProgress: 0.1,
    glow: 0.18,
    dropoutIntensity: 0.05,
    rescueIntensity: 0.12,
    cohortWindow: 0.28,
  },
  reminder: {
    heroProgress: 0.36,
    glow: 0.32,
    dropoutIntensity: 0.16,
    rescueIntensity: 0.44,
    cohortWindow: 0.48,
  },
  corridor: {
    heroProgress: 0.58,
    glow: 0.42,
    dropoutIntensity: 0.92,
    rescueIntensity: 0.2,
    cohortWindow: 0.68,
  },
  rescue: {
    heroProgress: 0.88,
    glow: 0.28,
    dropoutIntensity: 0.22,
    rescueIntensity: 0.9,
    cohortWindow: 0.9,
  },
};

const MAIN_PATH_POINTS = [
  [-8, 0.12, 4],
  [-5.5, 0.12, 2.8],
  [-2.8, 0.12, 1],
  [-0.4, 0.12, -1.5],
  [2.4, 0.12, -5.5],
  [5.4, 0.12, -9.4],
  [7.8, 0.12, -13.2],
];

const DROPOUT_PATH_POINTS = [
  [0.6, 0.02, -2.4],
  [2.2, -0.18, -3.6],
  [4.6, -0.62, -5.4],
  [7.2, -1.25, -6.5],
];

const CHECKPOINTS = [
  { id: 'dtp1', progress: 0.18, color: '#f5b042' },
  { id: 'dtp2', progress: 0.5, color: '#5a7bff' },
  { id: 'dtp3', progress: 0.87, color: '#47b7a0' },
];

const INTERVENTION_NODES = [
  { key: 'a1', label: 'SMS', position: [-6.8, 0.1, -11.4], color: '#f5b042' },
  { key: 'a2', label: 'CHW', position: [-2.3, 0.1, -12.1], color: '#47b7a0' },
  { key: 'a3', label: 'Recall', position: [2.2, 0.1, -12.1], color: '#5a7bff' },
  { key: 'a4', label: 'Incentive', position: [6.7, 0.1, -11.4], color: '#c6553a' },
];

const MAIN_CURVE = new CatmullRomCurve3(MAIN_PATH_POINTS.map(([x, y, z]) => new Vector3(x, y, z)));
const DROPOUT_CURVE = new CatmullRomCurve3(DROPOUT_PATH_POINTS.map(([x, y, z]) => new Vector3(x, y, z)));

const MAIN_TUBE = new TubeGeometry(MAIN_CURVE, 120, 0.36, 18, false);
const DROPOUT_TUBE = new TubeGeometry(DROPOUT_CURVE, 80, 0.22, 14, false);

export default function StableSimulationScene({ cameraMode = 'orbit', scale = 'community', chapter = 'home' }) {
  const interventions = useScenarioStore((s) => s.interventions);
  const cameraTargetRef = useRef(new Vector3());
  const chapterState = CHAPTER_STATES[chapter] || CHAPTER_STATES.home;

  const cohortFamilies = useMemo(() => {
    const count = {
      family: 6,
      community: 18,
      state: 28,
      nation: 40,
    }[scale] || 18;

    return Array.from({ length: count }, (_, index) => ({
      id: `family-${scale}-${index}`,
      phase: index * 0.37,
      size: 0.72 + (index % 3) * 0.08,
      atRisk: index % 4 === 0,
      dropped: index % 7 === 0,
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
      <color attach="background" args={['#091120']} />
      <fog attach="fog" args={['#0f1728', 12, 42]} />
      <ambientLight intensity={0.88} color="#c8d4ff" />
      <directionalLight position={[7, 11, 6]} intensity={1.45} color="#ffe4b3" />
      <pointLight position={[-7, 4, 6]} intensity={11} distance={24} color="#3058a3" />

      <EnvironmentPlate />
      <JourneyRibbon chapterState={chapterState} />
      <CheckpointGates chapterState={chapterState} />
      <InterventionStations interventions={interventions} chapterState={chapterState} />
      <HeroFamily chapterState={chapterState} chapter={chapter} />
      <CohortFamilies families={cohortFamilies} chapterState={chapterState} />
      <ClinicWorkers chapterState={chapterState} />
      <ClinicBackdrop />
    </>
  );
}

function EnvironmentPlate() {
  return (
    <>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, -3]}>
        <planeGeometry args={[54, 54]} />
        <meshStandardMaterial color="#08101b" />
      </mesh>
      <mesh position={[0, -0.35, -15]}>
        <boxGeometry args={[24, 5.5, 1]} />
        <meshStandardMaterial color="#111d30" />
      </mesh>
    </>
  );
}

function JourneyRibbon({ chapterState }) {
  const shimmerRef = useRef(null);

  useFrame((state) => {
    if (!shimmerRef.current) return;
    const opacity = 0.08 + chapterState.glow * 0.12 + (Math.sin(state.clock.elapsedTime * 1.8) * 0.5 + 0.5) * 0.05;
    shimmerRef.current.material.opacity = opacity;
  });

  return (
    <group>
      <mesh geometry={MAIN_TUBE}>
        <meshStandardMaterial color="#20324d" emissive="#35578d" emissiveIntensity={chapterState.glow * 0.45} />
      </mesh>
      <mesh geometry={DROPOUT_TUBE}>
        <meshStandardMaterial color="#231723" emissive="#a33f5f" emissiveIntensity={chapterState.dropoutIntensity * 0.55} />
      </mesh>
      <mesh ref={shimmerRef} geometry={MAIN_TUBE} scale={[1, 1.02, 1]}>
        <meshStandardMaterial color="#71a7ff" transparent opacity={0.08 + chapterState.glow * 0.12} />
      </mesh>
    </group>
  );
}

function CheckpointGates({ chapterState }) {
  const refs = useRef([]);

  useFrame((state) => {
    refs.current.forEach((group, index) => {
      if (!group) return;
      const pulse = 1 + (Math.sin(state.clock.elapsedTime * 2 + index) * 0.5 + 0.5) * 0.08;
      group.scale.setScalar(pulse);
    });
  });

  return (
    <group>
      {CHECKPOINTS.map((checkpoint, index) => {
        const point = MAIN_CURVE.getPointAt(checkpoint.progress);
        const pulse = checkpoint.id === 'dtp2'
          ? chapterState.dropoutIntensity
          : checkpoint.id === 'dtp3'
            ? chapterState.rescueIntensity
            : chapterState.glow;

        return (
          <group
            key={checkpoint.id}
            position={point}
            ref={(node) => {
              refs.current[index] = node;
            }}
          >
            <mesh position={[0, 2.1, 0]}>
              <torusGeometry args={[1.5, 0.12, 16, 40]} />
              <meshStandardMaterial color={checkpoint.color} emissive={checkpoint.color} emissiveIntensity={0.45 + pulse * 0.6} />
            </mesh>
            <mesh position={[0, 0.95, 0]}>
              <cylinderGeometry args={[0.08, 0.08, 1.8, 12]} />
              <meshStandardMaterial color={checkpoint.color} emissive={checkpoint.color} emissiveIntensity={0.18 + pulse * 0.25} />
            </mesh>
            <mesh position={[0, 2.95, 0]}>
              <boxGeometry args={[1.7, 0.12, 0.5]} />
              <meshStandardMaterial color="#dce5f0" emissive="#7f8a99" emissiveIntensity={0.08} />
            </mesh>
            <CheckpointTag checkpoint={checkpoint} pulse={pulse} />
          </group>
        );
      })}
    </group>
  );
}

function CheckpointTag({ checkpoint, pulse }) {
  const bars = checkpoint.id === 'dtp1' ? 4 : checkpoint.id === 'dtp2' ? 5 : 6;
  return (
    <group position={[0, 2.95, 0.28]}>
      {Array.from({ length: bars }).map((_, index) => (
        <mesh key={`${checkpoint.id}-${index}`} position={[-0.45 + index * 0.18, 0, 0]}>
          <boxGeometry args={[0.09, 0.12 + (index % 2) * 0.03, 0.04]} />
          <meshStandardMaterial
            color={checkpoint.color}
            emissive={checkpoint.color}
            emissiveIntensity={0.18 + pulse * 0.45}
          />
        </mesh>
      ))}
    </group>
  );
}

function InterventionStations({ interventions, chapterState }) {
  return (
    <group>
      {INTERVENTION_NODES.map((node) => (
        <InterventionStation
          key={node.key}
          active={!!interventions[node.key]}
          color={node.color}
          label={node.label}
          position={node.position}
          rescueIntensity={chapterState.rescueIntensity}
        />
      ))}
    </group>
  );
}

function InterventionStation({ active, color, label, position, rescueIntensity }) {
  const groupRef = useRef(null);
  const ringColor = useMemo(() => new Color(color), [color]);
  const bars = Math.max(3, Math.min(label.length, 8));

  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime;
    groupRef.current.position.y = position[1] + Math.sin(t * 1.7 + position[0]) * 0.08;
    groupRef.current.rotation.y += active ? 0.016 : 0.008;
  });

  return (
    <group ref={groupRef} position={position}>
      <mesh>
        <cylinderGeometry args={[0.48, 0.48, active ? 2 : 1.15, 24]} />
        <meshStandardMaterial
          color={active ? color : '#354255'}
          emissive={active ? color : '#141c2a'}
          emissiveIntensity={active ? 0.35 + rescueIntensity * 0.5 : 0.08}
        />
      </mesh>
      <mesh position={[0, active ? 1.15 : 0.7, 0]}>
        <torusGeometry args={[0.92, 0.08, 16, 40]} />
        <meshStandardMaterial color={ringColor} emissive={ringColor} emissiveIntensity={active ? 0.5 + rescueIntensity * 0.55 : 0.12} />
      </mesh>
      <mesh position={[0, -0.2, 0]}>
        <circleGeometry args={[1.5, 40]} />
        <meshStandardMaterial color={ringColor} transparent opacity={active ? 0.16 + rescueIntensity * 0.12 : 0.05} />
      </mesh>
      <group position={[0, active ? 2.05 : 1.45, 0.25]}>
        {Array.from({ length: bars }).map((_, index) => (
          <mesh key={`${label}-${index}`} position={[-0.52 + index * 0.16, 0, 0]}>
            <boxGeometry args={[0.08, 0.1 + (index % 3) * 0.03, 0.04]} />
            <meshStandardMaterial color={ringColor} emissive={ringColor} emissiveIntensity={active ? 0.35 : 0.08} />
          </mesh>
        ))}
      </group>
    </group>
  );
}

function HeroFamily({ chapterState, chapter }) {
  const isDropped = chapter === 'corridor';
  const groupRef = useRef(null);
  const haloRef = useRef(null);
  const burstRef = useRef(null);

  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime;
    const pulse = Math.sin(t * 0.8) * 0.018;
    const mainProgress = Math.min(0.97, Math.max(0.03, chapterState.heroProgress + pulse));
    const path = isDropped ? DROPOUT_CURVE : MAIN_CURVE;
    const progress = isDropped
      ? 0.34 + (Math.sin(t * 0.7) * 0.5 + 0.5) * 0.22
      : mainProgress;
    const point = path.getPointAt(progress);
    const ahead = path.getPointAt(Math.min(0.99, progress + 0.03));
    const direction = ahead.clone().sub(point).normalize();
    const angle = Math.atan2(direction.x, direction.z);

    groupRef.current.position.set(point.x, point.y, point.z);
    groupRef.current.rotation.set(0, angle, 0);

    if (haloRef.current) {
      const scale = 1 + (Math.sin(t * 2.3) * 0.5 + 0.5) * chapterState.rescueIntensity * 0.28;
      haloRef.current.scale.setScalar(scale);
    }

    if (burstRef.current) {
      burstRef.current.rotation.y += 0.03;
      const scale = 1 + (Math.sin(t * 3.1) * 0.5 + 0.5) * chapterState.dropoutIntensity * 0.18;
      burstRef.current.scale.setScalar(scale);
    }
  });

  return (
    <group ref={groupRef}>
      <FamilyUnit
        emphasis={0.28 + chapterState.glow * 0.38}
        childDrop={isDropped ? -0.85 : 0}
        rescued={chapter === 'rescue'}
        childScale={0.78}
        motherScale={1.18}
      />
      {isDropped && (
        <DropoutBurst ref={burstRef} position={[0.1, -0.55, 0.1]} intensity={chapterState.dropoutIntensity} />
      )}
      {chapter === 'rescue' && (
        <RescueHalo ref={haloRef} position={[0, 2.1, 0]} intensity={chapterState.rescueIntensity} />
      )}
    </group>
  );
}

function CohortFamilies({ families, chapterState }) {
  const refs = useRef([]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    families.forEach((family, index) => {
      const group = refs.current[index];
      if (!group) return;

      const travel = (t * (0.035 + (family.phase % 5) * 0.003) + family.phase * 0.09) % 1;
      const onDropout = family.dropped && travel < chapterState.cohortWindow;
      const progress = onDropout
        ? Math.min(0.98, 0.16 + travel * 0.7)
        : Math.min(0.98, 0.04 + travel * 0.92);
      const path = onDropout ? DROPOUT_CURVE : MAIN_CURVE;
      const point = path.getPointAt(progress);
      const ahead = path.getPointAt(Math.min(0.99, progress + 0.025));
      const direction = ahead.clone().sub(point).normalize();
      const angle = Math.atan2(direction.x, direction.z);
      const bob = Math.sin(t * 3.4 + family.phase) * 0.045;

      group.position.set(point.x, point.y + bob, point.z);
      group.rotation.set(0, angle, 0);
      group.scale.setScalar(family.size);
    });
  });

  return (
    <group>
      {families.map((family, index) => {
        const rescueBoost = family.atRisk ? chapterState.rescueIntensity : 0;
        const likelyDropped = family.dropped && chapterState.cohortWindow > 0.45;

        return (
          <group
            key={family.id}
            ref={(node) => {
              refs.current[index] = node;
            }}
          >
            <FamilyUnit
              emphasis={0.08 + rescueBoost * 0.16}
              childDrop={likelyDropped ? -0.45 : 0}
              rescued={rescueBoost > 0.35}
              childScale={0.56}
              motherScale={0.9}
              muted={!family.atRisk && chapterState.cohortWindow < 0.4}
            />
            {likelyDropped && (
              <DropoutBurst position={[0, -0.28, 0]} intensity={chapterState.dropoutIntensity * 0.55} small />
            )}
          </group>
        );
      })}
    </group>
  );
}

function ClinicWorkers({ chapterState }) {
  const workers = useMemo(
    () => [
      { id: 'w1', base: new Vector3(-5.5, 0, -13.7), amp: 0.9, speed: 0.55, color: '#47b7a0' },
      { id: 'w2', base: new Vector3(-0.8, 0, -14.2), amp: 1.2, speed: 0.7, color: '#5a7bff' },
      { id: 'w3', base: new Vector3(4.9, 0, -13.5), amp: 0.85, speed: 0.62, color: '#f5b042' },
    ],
    []
  );
  const refs = useRef([]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    workers.forEach((worker, index) => {
      const group = refs.current[index];
      if (!group) return;
      const x = worker.base.x + Math.sin(t * worker.speed + index) * worker.amp;
      const z = worker.base.z + Math.cos(t * worker.speed * 0.8 + index) * 0.55;
      group.position.set(x, worker.base.y, z);
      group.rotation.set(0, Math.sin(t * worker.speed + index) * 0.35, 0);
    });
  });

  return (
    <group>
      {workers.map((worker, index) => (
        <group
          key={worker.id}
          ref={(node) => {
            refs.current[index] = node;
          }}
        >
          <Person position={[0, 0, 0]} scale={1} body={worker.color} skirt="#243650" glow={0.18 + chapterState.rescueIntensity * 0.2} />
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.08, 0]}>
            <ringGeometry args={[0.36, 0.5, 28]} />
            <meshStandardMaterial color={worker.color} emissive={worker.color} emissiveIntensity={0.28 + chapterState.rescueIntensity * 0.24} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function FamilyUnit({
  emphasis = 0.2,
  childDrop = 0,
  rescued = false,
  childScale = 0.72,
  motherScale = 1.1,
  muted = false,
}) {
  const motherColor = muted ? '#d2d7e2' : '#f5b042';
  const childColor = rescued ? '#47b7a0' : muted ? '#c9cfdb' : '#c6553a';

  return (
    <group>
      <Person position={[-0.34, 0, 0]} scale={motherScale} body={motherColor} skirt="#74441f" glow={emphasis} />
      <Person position={[0.48, Math.max(-1.1, childDrop), 0.2]} scale={childScale} body={childColor} skirt={childColor} glow={rescued ? emphasis + 0.22 : emphasis * 0.7} />
      <mesh position={[0.08, 0.84 + Math.max(-0.5, childDrop * 0.25), 0.05]} rotation={[0, 0, Math.PI / 2]}>
        <capsuleGeometry args={[0.03, 0.72, 4, 8]} />
        <meshStandardMaterial color={rescued ? '#47b7a0' : '#8d98aa'} emissive={rescued ? '#47b7a0' : '#000000'} emissiveIntensity={rescued ? 0.35 : 0} />
      </mesh>
    </group>
  );
}

const DropoutBurst = forwardRef(function DropoutBurst({ position, intensity, small = false }, ref) {
  return (
    <group ref={ref} position={position}>
      {Array.from({ length: small ? 4 : 6 }).map((_, index) => (
        <mesh
          key={`drop-${index}`}
          position={[
            Math.cos((index / 6) * Math.PI * 2) * (small ? 0.35 : 0.5),
            0,
            Math.sin((index / 6) * Math.PI * 2) * (small ? 0.35 : 0.5),
          ]}
          rotation={[-Math.PI / 2, 0, index * 0.4]}
        >
          <ringGeometry args={[small ? 0.12 : 0.16, small ? 0.17 : 0.22, 18]} />
          <meshStandardMaterial color="#c6553a" emissive="#c6553a" emissiveIntensity={0.18 + intensity * 0.4} transparent opacity={0.22 + intensity * 0.18} />
        </mesh>
      ))}
    </group>
  );
});

const RescueHalo = forwardRef(function RescueHalo({ position, intensity }, ref) {
  return (
    <group ref={ref} position={position}>
      <mesh>
        <torusGeometry args={[1.1, 0.1, 18, 48]} />
        <meshStandardMaterial color="#47b7a0" emissive="#47b7a0" emissiveIntensity={0.45 + intensity * 0.55} />
      </mesh>
      <mesh position={[0, -0.95, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.85, 1.25, 28]} />
        <meshStandardMaterial color="#47b7a0" transparent opacity={0.12 + intensity * 0.12} />
      </mesh>
    </group>
  );
});

function ClinicBackdrop() {
  return (
    <group position={[0, 0, -15.2]}>
      <mesh position={[0, 2.8, 0]}>
        <boxGeometry args={[19, 5.5, 1]} />
        <meshStandardMaterial color="#121f34" />
      </mesh>
      <mesh position={[-5.5, 2.9, 0.55]}>
        <boxGeometry args={[3.8, 2.5, 0.15]} />
        <meshStandardMaterial color="#1b2c44" emissive="#395783" emissiveIntensity={0.1} />
      </mesh>
      <mesh position={[0, 2.9, 0.55]}>
        <boxGeometry args={[3.8, 2.5, 0.15]} />
        <meshStandardMaterial color="#17253b" emissive="#334f79" emissiveIntensity={0.08} />
      </mesh>
      <mesh position={[5.5, 2.9, 0.55]}>
        <boxGeometry args={[3.8, 2.5, 0.15]} />
        <meshStandardMaterial color="#1b2c44" emissive="#395783" emissiveIntensity={0.1} />
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
      <mesh position={[0, 1.08, 0]}>
        <capsuleGeometry args={[0.22, 0.92, 4, 8]} />
        <meshStandardMaterial color={body} emissive={glow > 0 ? '#f5b042' : '#000000'} emissiveIntensity={glow} />
      </mesh>
      <mesh position={[0, 0.3, 0]}>
        <coneGeometry args={[0.35, 0.72, 6]} />
        <meshStandardMaterial color={skirt} />
      </mesh>
    </group>
  );
}
