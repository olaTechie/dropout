import { EffectComposer, Bloom, DepthOfField, Vignette, Noise } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';

export default function Effects({ enabled = true }) {
  if (!enabled) return null;
  return (
    <EffectComposer>
      <Bloom intensity={0.6} luminanceThreshold={0.85} luminanceSmoothing={0.2} />
      <DepthOfField focusDistance={0.02} focalLength={0.05} bokehScale={2} />
      <Vignette eskil={false} offset={0.2} darkness={0.7} />
      <Noise opacity={0.05} blendFunction={BlendFunction.OVERLAY} />
    </EffectComposer>
  );
}
