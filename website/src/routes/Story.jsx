import { useState } from 'react';
import { Scrollama, Step } from 'react-scrollama';
import StageCanvas from '../scene/StageCanvas.jsx';
import CinematicRig from '../scene/camera/CinematicRig.jsx';
import LightRig from '../scene/lighting/LightRig.jsx';
import Effects from '../scene/effects/Effects.jsx';
import ActI_Family from '../scene/acts/ActI_Family.jsx';
import { useStoryStore } from '../state/story.js';

export default function Story() {
  const [progress, setProgress] = useState(0);
  const currentAct = useStoryStore((s) => s.currentAct);
  const setAct = useStoryStore((s) => s.setAct);

  return (
    <>
      <StageCanvas>
        <LightRig act={currentAct} />
        {currentAct === 1 && <ActI_Family progress={progress} />}
        <CinematicRig act={currentAct} />
        <Effects />
      </StageCanvas>

      <div className="relative z-10">
        <Scrollama onStepEnter={({ data }) => setAct(data)} onStepProgress={({ progress: p }) => setProgress(p)}>
          <Step data={1}>
            <section className="min-h-[200vh] flex items-center justify-center px-6">
              <div className="max-w-xl text-center">
                <h2 className="font-serif text-5xl md:text-7xl leading-tight">
                  Six weeks from birth, a decision begins.
                </h2>
                <p className="mt-8 text-muted">
                  In a home like this, across Nigeria, every year, 4.9 million children reach this moment.
                </p>
              </div>
            </section>
          </Step>
        </Scrollama>
      </div>
    </>
  );
}
