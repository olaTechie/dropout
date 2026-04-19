import { lazy, Suspense } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import Shell from './components/layout/Shell.jsx';
import Landing from './routes/Landing.jsx';
import Transcript from './routes/Transcript.jsx';

// Heavy 3D routes are lazy-loaded
const Story = lazy(() => import('./routes/Story.jsx'));
const Simulation = lazy(() => import('./routes/Simulation.jsx'));
// Charts-heavy routes (recharts, d3) lazy-loaded so Landing doesn't ship them
const Policy = lazy(() => import('./routes/Policy.jsx'));
const Explorer = lazy(() => import('./routes/Explorer.jsx'));
const Methods = lazy(() => import('./routes/Methods.jsx'));

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
      <Route path="/story" element={<Shell><Suspense fallback={<Loader />}><Story /></Suspense></Shell>} />
      <Route path="/story/transcript" element={<Shell><Transcript /></Shell>} />
      <Route path="/policy" element={<Shell><Suspense fallback={<Loader />}><Policy /></Suspense></Shell>} />
      <Route path="/simulation" element={<Shell><Suspense fallback={<Loader />}><Simulation /></Suspense></Shell>} />
      <Route path="/explorer" element={<Shell><Suspense fallback={<Loader />}><Explorer /></Suspense></Shell>} />
      <Route path="/explorer/methods" element={<Shell><Suspense fallback={<Loader />}><Methods /></Suspense></Shell>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
