export default function Child({ position = [0, 0, 0], scale = 1, color = '#D4A574', glow = 0 }) {
  return (
    <group position={position} scale={scale}>
      <mesh castShadow position={[0, 0.55, 0]}>
        <sphereGeometry args={[0.15, 12, 12]} />
        <meshStandardMaterial color={color} emissive={glow > 0 ? '#F5B042' : '#000'} emissiveIntensity={glow} />
      </mesh>
      <mesh castShadow position={[0, 0.25, 0]}>
        <capsuleGeometry args={[0.12, 0.35, 4, 8]} />
        <meshStandardMaterial color="#C6553A" />
      </mesh>
    </group>
  );
}
