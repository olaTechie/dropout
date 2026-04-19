export default function Clinic({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      <mesh castShadow receiveShadow position={[0, 1, 0]}>
        <boxGeometry args={[3.5, 2, 2.5]} />
        <meshStandardMaterial color="#F4F0E6" roughness={0.7} />
      </mesh>
      <mesh position={[0, 2.1, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 0.6, 8]} />
        <meshStandardMaterial color="#47B7A0" />
      </mesh>
      <mesh position={[0, 2.5, 0]}>
        <boxGeometry args={[0.6, 0.1, 0.1]} />
        <meshStandardMaterial color="#47B7A0" />
      </mesh>
    </group>
  );
}
