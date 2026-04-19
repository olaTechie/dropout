import { OrbitControls } from '@react-three/drei';

export default function OrbitRig({ enabled = true }) {
  return <OrbitControls enabled={enabled} enablePan={true} enableZoom={true} maxDistance={100} minDistance={2} />;
}
