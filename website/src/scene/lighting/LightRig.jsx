const ACT_LIGHTING = {
  1: { keyColor: '#FFD3A0', intensity: 1.2, ambient: '#3A2A1A', ambientIntensity: 0.3 },
  2: { keyColor: '#F4F0E6', intensity: 1.0, ambient: '#1A2340', ambientIntensity: 0.4 },
  3: { keyColor: '#A5BFFF', intensity: 0.9, ambient: '#0D1220', ambientIntensity: 0.3 },
  4: { keyColor: '#FFD3A0', intensity: 1.1, ambient: '#1A2340', ambientIntensity: 0.4 },
  5: { keyColor: '#4A5568', intensity: 0.4, ambient: '#05070C', ambientIntensity: 0.2 },
};

export default function LightRig({ act = 1 }) {
  const lk = ACT_LIGHTING[act] || ACT_LIGHTING[1];
  return (
    <>
      <ambientLight intensity={lk.ambientIntensity} color={lk.ambient} />
      <directionalLight
        position={[5, 8, 4]}
        intensity={lk.intensity}
        color={lk.keyColor}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <hemisphereLight intensity={0.15} groundColor="#05070C" color={lk.keyColor} />
    </>
  );
}
