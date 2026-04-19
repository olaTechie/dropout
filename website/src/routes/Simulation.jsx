import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import StageCanvas from '../scene/StageCanvas.jsx';
import LightRig from '../scene/lighting/LightRig.jsx';
import OrbitRig from '../scene/camera/OrbitRig.jsx';
import ActIV_Interventions from '../scene/acts/ActIV_Interventions.jsx';
import SimulationControls from '../components/hud/SimulationControls.jsx';
import { useScenarioStore } from '../state/scenario.js';

export default function Simulation() {
  const [cameraMode, setCameraMode] = useState('orbit');
  const [scale, setScale] = useState('community');
  const [params] = useSearchParams();

  useEffect(() => {
    if (params.toString()) {
      useScenarioStore.getState().decodeFromURL(params.toString());
    }
  }, [params]);

  return (
    <>
      <StageCanvas className="fixed inset-0 -z-0" shadows={false}>
        <LightRig act={4} />
        <ActIV_Interventions progress={0.5} />
        <OrbitRig enabled={cameraMode === 'orbit'} />
      </StageCanvas>
      <SimulationControls cameraMode={cameraMode} setCameraMode={setCameraMode} scale={scale} setScale={setScale} />
    </>
  );
}
