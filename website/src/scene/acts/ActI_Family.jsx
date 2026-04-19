import { useRef } from 'react';
import { ContactShadows } from '@react-three/drei';
import Mother from '../props/Mother.jsx';
import Child from '../props/Child.jsx';
import Home from '../props/Home.jsx';

// We deliberately do NOT use drei's <Environment preset="..."> here —
// drei fetches the HDRI from an external CDN (market.pmnd.rs), which the
// strict CSP in index.html blocks. Lighting comes from <LightRig />
// (added by Story.jsx); without an Environment we lose image-based
// reflections on PBR materials but keep the scene fully self-hosted.
export default function ActI_Family({ progress = 0 }) {
  const glowRef = useRef(0);
  glowRef.current = progress > 0.5 ? (progress - 0.5) * 2 : 0;

  return (
    <>
      <fog attach="fog" args={['#0D1220', 5, 25]} />

      <Home position={[-3, 0, -2]} />

      <Mother position={[0, 0, 0]} />
      <Child position={[0.3, 0, 0.4]} scale={0.7} glow={glowRef.current} />

      <ContactShadows position={[0, 0.01, 0]} opacity={0.5} scale={10} blur={2} far={4} />

      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[40, 40]} />
        <meshStandardMaterial color="#1A2340" />
      </mesh>
    </>
  );
}
