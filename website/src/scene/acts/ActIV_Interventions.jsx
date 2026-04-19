import { useScenarioStore } from '../../state/scenario.js';
import Cohort from '../props/Cohort.jsx';
import InterventionEffect from '../props/InterventionEffect.jsx';

export default function ActIV_Interventions({ progress = 0 }) {
  const interventions = useScenarioStore((s) => s.interventions);

  return (
    <>
      <fog attach="fog" args={['#1A2340', 8, 50]} />

      <Cohort count={100} progress={progress * 0.5} spread={8} />

      <InterventionEffect type="a1" active={interventions.a1} position={[0, 1, 5]} />
      <InterventionEffect type="a2" active={interventions.a2} position={[0, 1, 0]} />
      <InterventionEffect type="a3" active={interventions.a3} position={[0, 1, -5]} />
      <InterventionEffect type="a4" active={interventions.a4} position={[0, 1, -10]} />

      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[60, 60]} />
        <meshStandardMaterial color="#0D1220" />
      </mesh>
    </>
  );
}
