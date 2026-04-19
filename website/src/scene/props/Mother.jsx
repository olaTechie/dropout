export default function Mother({ position = [0, 0, 0], scale = 1 }) {
  return (
    <group position={position} scale={scale}>
      <mesh castShadow position={[0, 1.65, 0]}>
        <sphereGeometry args={[0.18, 12, 12]} />
        <meshStandardMaterial color="#A66A2C" />
      </mesh>
      <mesh castShadow position={[0, 1.1, 0]}>
        <capsuleGeometry args={[0.22, 0.9, 4, 8]} />
        <meshStandardMaterial color="#F5B042" />
      </mesh>
      <mesh castShadow position={[0, 0.3, 0]}>
        <coneGeometry args={[0.35, 0.7, 6]} />
        <meshStandardMaterial color="#7A4A1E" />
      </mesh>
    </group>
  );
}
