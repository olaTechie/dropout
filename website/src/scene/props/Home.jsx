export default function Home({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      <mesh castShadow receiveShadow position={[0, 0.75, 0]}>
        <boxGeometry args={[2.5, 1.5, 2]} />
        <meshStandardMaterial color="#A66A2C" roughness={0.9} />
      </mesh>
      <mesh castShadow position={[0, 1.8, 0]} rotation={[0, Math.PI / 4, 0]}>
        <coneGeometry args={[2, 0.8, 4]} />
        <meshStandardMaterial color="#7A4A1E" roughness={0.8} />
      </mesh>
      <mesh position={[0, 0.7, 1.01]}>
        <boxGeometry args={[0.5, 0.9, 0.02]} />
        <meshStandardMaterial color="#F5B042" emissive="#F5B042" emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
}
