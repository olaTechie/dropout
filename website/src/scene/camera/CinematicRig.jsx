import { useThree, useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import { Vector3 } from 'three';
import { useReducedMotion } from '../../hooks/useReducedMotion.js';

const ACT_KEYS = {
  1: { pos: [0, 1.5, 4], look: [0, 1.3, 0] },
  2: { pos: [0, 3, 6], look: [0, 1.5, 0] },
  3: { pos: [0, 50, 40], look: [0, 0, 0] },
  4: { pos: [0, 4, 8], look: [0, 1.5, 0] },
  5: { pos: [0, 8, 12], look: [0, 2, 0] },
};

export default function CinematicRig({ act }) {
  const { camera } = useThree();
  const targetPos = useRef(new Vector3());
  const targetLook = useRef(new Vector3());
  const reduced = useReducedMotion();

  useFrame((_, dt) => {
    const key = ACT_KEYS[act] || ACT_KEYS[1];
    targetPos.current.set(...key.pos);
    targetLook.current.set(...key.look);
    if (reduced) {
      camera.position.copy(targetPos.current);
    } else {
      camera.position.lerp(targetPos.current, Math.min(1, dt * 0.8));
    }
    camera.lookAt(targetLook.current);
  });

  return null;
}
