import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter } from 'react-router-dom';
import App from './App.jsx';
import './styles/globals.css';

// HashRouter (URLs of the form /dropout/#/policy) deliberately avoids the
// GitHub Pages 404.html SPA fallback hack. Removing that hack also removes
// the inline routing shim that previously sat in index.html, which lets us
// run with a strict CSP (see <meta http-equiv> in index.html). HashRouter
// is path-depth-agnostic, so the app no longer depends on the deploy being
// exactly one segment deep at /dropout/.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </StrictMode>
);
