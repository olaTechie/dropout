import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Scrollama, Step } from 'react-scrollama';
import { hasWebGL } from '../lib/webgl.js';
import StageCanvas from '../scene/StageCanvas.jsx';
import StableStoryScene from '../scene/StableStoryScene.jsx';
import InterventionPanel from '../components/hud/InterventionPanel.jsx';
import DashboardOverlay from '../components/hud/DashboardOverlay.jsx';
import CanvasErrorBoundary from '../components/shared/CanvasErrorBoundary.jsx';
import { useStoryStore } from '../state/story.js';

export default function Story() {
  // All hooks before any conditional return — React Rules of Hooks
  const [progress, setProgress] = useState(0);
  const currentAct = useStoryStore((s) => s.currentAct);
  const setAct = useStoryStore((s) => s.setAct);

  if (!hasWebGL()) {
    return <Navigate to="/story/transcript" replace />;
  }

  return (
    <>
      <CanvasErrorBoundary>
        <StageCanvas>
          <StableStoryScene act={currentAct} progress={progress} />
        </StageCanvas>
      </CanvasErrorBoundary>

      {currentAct === 4 && <InterventionPanel />}
      {currentAct === 5 && <DashboardOverlay visible />}

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
          <Step data={2}>
            <section className="min-h-[200vh] flex items-center justify-center px-6">
              <div className="max-w-xl text-center">
                <h2 className="font-serif text-5xl md:text-7xl leading-tight">The corridor.</h2>
                <p className="mt-8 text-muted">
                  By their first birthday, 15 of every 100 never made it.
                </p>
              </div>
            </section>
          </Step>
          <Step data={3}>
            <section className="min-h-[200vh] flex items-center justify-center px-6">
              <div className="max-w-xl text-center">
                <h2 className="font-serif text-5xl md:text-7xl leading-tight">A nation of corridors.</h2>
                <p className="mt-8 text-muted">
                  Across 774 LGAs, millions of cohorts move through the same 6-10-14 week gates.
                </p>
              </div>
            </section>
          </Step>
          <Step data={4}>
            <section className="min-h-[200vh] flex items-center justify-center px-6">
              <div className="max-w-xl text-center">
                <h2 className="font-serif text-5xl md:text-7xl leading-tight">What if we acted?</h2>
                <p className="mt-8 text-muted">
                  Toggle interventions on the left. SMS, CHW, recall, incentive — each has a cost and a reach.
                </p>
              </div>
            </section>
          </Step>
          <Step data={5}>
            <section className="min-h-[200vh] flex items-center justify-center px-6">
              <div className="max-w-xl text-center">
                <h2 className="font-serif text-5xl md:text-7xl leading-tight">A policy emerges.</h2>
                <p className="mt-8 text-muted">
                  Risk-targeted CHW outreach, underwritten by SMS at scale.
                </p>
              </div>
            </section>
          </Step>
        </Scrollama>
      </div>
    </>
  );
}
