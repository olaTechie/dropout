import { useEffect, useState } from 'react';
import { Navigate, useSearchParams } from 'react-router-dom';
import { hasWebGL } from '../lib/webgl.js';
import StageCanvas from '../scene/StageCanvas.jsx';
import LightRig from '../scene/lighting/LightRig.jsx';
import OrbitRig from '../scene/camera/OrbitRig.jsx';
import ActIV_Interventions from '../scene/acts/ActIV_Interventions.jsx';
import SimulationControls from '../components/hud/SimulationControls.jsx';
import CanvasErrorBoundary from '../components/shared/CanvasErrorBoundary.jsx';
import { useScenarioStore } from '../state/scenario.js';

export default function Simulation() {
  // All hooks before the conditional return — React Rules of Hooks
  const [cameraMode, setCameraMode] = useState('orbit');
  const [scale, setScale] = useState('community');
  const [params] = useSearchParams();

  useEffect(() => {
    if (params.toString()) {
      useScenarioStore.getState().decodeFromURL(params.toString());
    }
  }, [params]);

  // Same WebGL capability gate as /story — without WebGL the canvas would
  // boot to a blank or broken state, so route the user to /policy where
  // the same scenario data is rendered as static charts and tables.
  if (!hasWebGL()) {
    return <Navigate to="/policy" replace state={{ reason: 'no-webgl' }} />;
  }

  return (
    <>
      <CanvasErrorBoundary>
        <StageCanvas className="fixed inset-0 -z-0" shadows={false}>
          <LightRig act={4} />
          <ActIV_Interventions progress={0.5} />
          <OrbitRig enabled={cameraMode === 'orbit'} />
        </StageCanvas>
      </CanvasErrorBoundary>
      <SimulationControls cameraMode={cameraMode} setCameraMode={setCameraMode} scale={scale} setScale={setScale} />
    </>
  );
}
