import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Shell from './components/layout/Shell.jsx';
import Landing from './routes/Landing.jsx';
import Policy from './routes/Policy.jsx';
import Explorer from './routes/Explorer.jsx';
import Methods from './routes/Methods.jsx';
import Transcript from './routes/Transcript.jsx';

// Heavy 3D routes are lazy-loaded
const Story = lazy(() => import('./routes/Story.jsx'));
const Simulation = lazy(() => import('./routes/Simulation.jsx'));

function Loader() {
  return (
    <div className="min-h-screen flex items-center justify-center text-muted">
      Loading the cinematic…
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Shell><Landing /></Shell>} />
      <Route path="/story" element={<Shell showChrome={false}><Suspense fallback={<Loader />}><Story /></Suspense></Shell>} />
      <Route path="/story/transcript" element={<Shell><Transcript /></Shell>} />
      <Route path="/policy" element={<Shell><Policy /></Shell>} />
      <Route path="/simulation" element={<Shell showChrome={false}><Suspense fallback={<Loader />}><Simulation /></Suspense></Shell>} />
      <Route path="/explorer" element={<Shell><Explorer /></Shell>} />
      <Route path="/explorer/methods" element={<Shell><Methods /></Shell>} />
    </Routes>
  );
}
