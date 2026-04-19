import { OrbitControls } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import { Vector3 } from 'three';

const CAMERA_MODES = {
  orbit: {
    position: new Vector3(0, 6, 14),
    target: new Vector3(0, 0.8, -2),
    controls: true,
  },
  flythrough: {
    position: new Vector3(0, 2.4, 5.5),
    target: new Vector3(0, 1.2, -14),
    controls: false,
  },
  top: {
    position: new Vector3(0, 24, 0.01),
    target: new Vector3(0, 0, -4),
    controls: false,
  },
};

export default function OrbitRig({ mode = 'orbit' }) {
  const controlsRef = useRef(null);

  useFrame((state) => {
    const config = CAMERA_MODES[mode] || CAMERA_MODES.orbit;
    state.camera.position.lerp(config.position, 0.08);

    if (config.controls && controlsRef.current) {
      controlsRef.current.target.lerp(config.target, 0.12);
      controlsRef.current.update();
      return;
    }

    state.camera.lookAt(config.target);
  });

  return (
    <OrbitControls
      ref={controlsRef}
      enabled={(CAMERA_MODES[mode] || CAMERA_MODES.orbit).controls}
      enablePan
      enableZoom
      maxDistance={100}
      minDistance={2}
    />
  );
}
