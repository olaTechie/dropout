# Cinematic Dropout Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a cinematic interactive website for the Nigeria DTP vaccine dropout study with 4 routes (Story, Policy, Simulation, Explorer), 5-act Three.js hero journey, pre-computed scenario interpolation, and WCAG AA accessibility.

**Architecture:** Vite + React 19 + React Three Fiber monorepo single-app. Route-level code splitting puts heavy 3D assets on `/story` and `/simulation` lazy chunks, keeping `/policy` and `/explorer` fast. Zustand stores sync scene + UI. Pre-computed scenario cube (225 configs) trilinearly interpolated client-side for what-if sliders. Deploys to GitHub Pages at `olatechie.github.io/dropout/`.

**Tech Stack:** Vite 8 · React 19 · react-router-dom 7 · @react-three/fiber 9 · @react-three/drei 10 · @react-three/postprocessing · zustand 5 · framer-motion 12 · d3 7 · recharts 3 · tailwindcss 4 · react-scrollama 2 · vitest · @testing-library/react · @axe-core/react

**Working directory:** `/Users/uthlekan/Library/CloudStorage/Dropbox/00Todo/00_ToReview/vacSeries/03_dropout`

**Output directory:** `website/` (new, adjacent to existing `manuscript/` and `src/`)

---

## Phase 1: Scaffold · Data · Policy MVP (Week 1)

### Task 1: Scaffold Vite project with dependencies

**Files:**
- Create: `website/package.json`
- Create: `website/vite.config.js`
- Create: `website/index.html`
- Create: `website/.gitignore`
- Create: `website/src/main.jsx`
- Create: `website/src/App.jsx`
- Create: `website/src/styles/globals.css`

- [ ] **Step 1: Create directory and package.json**

Run:
```bash
mkdir -p website/src website/public/data website/public/models website/public/textures website/public/fonts website/scripts
```

Create `website/package.json`:

```json
{
  "name": "dropout-website",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "lint": "eslint .",
    "deploy": "gh-pages -d dist"
  },
  "dependencies": {
    "@react-three/drei": "^10.7.7",
    "@react-three/fiber": "^9.5.0",
    "@react-three/postprocessing": "^2.16.0",
    "d3": "^7.9.0",
    "framer-motion": "^12.38.0",
    "lucide-react": "^0.475.0",
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "react-router-dom": "^7.14.0",
    "react-scrollama": "^2.4.2",
    "react-simple-maps": "^3.0.0",
    "recharts": "^3.8.1",
    "three": "^0.183.2",
    "topojson-client": "^3.1.0",
    "zustand": "^5.0.12"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.2.2",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.3.0",
    "@testing-library/user-event": "^14.5.2",
    "@vitejs/plugin-react": "^6.0.1",
    "@types/react": "^19.2.14",
    "@types/react-dom": "^19.2.3",
    "eslint": "^9.39.4",
    "gh-pages": "^6.3.0",
    "jsdom": "^26.0.0",
    "tailwindcss": "^4.2.2",
    "vite": "^8.0.1",
    "vitest": "^3.0.0"
  }
}
```

- [ ] **Step 2: Create Vite config**

Create `website/vite.config.js`:

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/dropout/',
  build: {
    target: 'es2022',
    rollupOptions: {
      output: {
        manualChunks: {
          'three-core': ['three'],
          'three-react': [
            '@react-three/fiber',
            '@react-three/drei',
            '@react-three/postprocessing',
          ],
          'charts': ['d3', 'recharts'],
          'motion': ['framer-motion'],
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.js'],
  },
});
```

- [ ] **Step 3: Create index.html and entry**

Create `website/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/dropout/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Reducing DTP vaccination dropout in Nigeria — an interactive story and policy explorer from the University of Warwick." />
    <title>Catching the Fall — DTP Dropout in Nigeria</title>
  </head>
  <body class="bg-[#05070C] text-[#F4F0E6]">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

Create `website/src/main.jsx`:

```jsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import './styles/globals.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter basename="/dropout">
      <App />
    </BrowserRouter>
  </StrictMode>
);
```

Create `website/src/App.jsx`:

```jsx
import { Routes, Route } from 'react-router-dom';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<div className="p-8">Scaffold ready</div>} />
    </Routes>
  );
}
```

Create `website/src/styles/globals.css`:

```css
@import "tailwindcss";

@theme {
  --color-abyss: #05070C;
  --color-night: #0D1220;
  --color-dusk: #1A2340;
  --color-moonlight: #F4F0E6;
  --color-muted: #9AA3B8;
  --color-saffron: #F5B042;
  --color-terracotta: #C6553A;
  --color-iris: #5A7BFF;
  --color-verdigris: #47B7A0;
  --color-ochre: #A66A2C;
  --font-serif: "Fraunces", serif;
  --font-sans: "Inter", sans-serif;
  --font-mono: "JetBrains Mono", monospace;
}

html, body, #root { height: 100%; }
body { font-family: var(--font-sans); }
```

Create `website/src/test-setup.js`:

```js
import '@testing-library/jest-dom';
```

Create `website/.gitignore`:

```
node_modules
dist
.vite
*.log
.DS_Store
```

- [ ] **Step 4: Install and verify**

Run:
```bash
cd website && npm install && npm run dev
```

Expected: dev server starts on http://localhost:5173/dropout/ showing "Scaffold ready".

- [ ] **Step 5: Commit**

```bash
git add website/
git commit -m "feat(web): scaffold Vite + React 19 + R3F + Zustand + Tailwind"
```

---

### Task 2: Router shell + 4 route stubs + layout

**Files:**
- Create: `website/src/routes/Landing.jsx`
- Create: `website/src/routes/Story.jsx`
- Create: `website/src/routes/Policy.jsx`
- Create: `website/src/routes/Simulation.jsx`
- Create: `website/src/routes/Explorer.jsx`
- Create: `website/src/routes/Methods.jsx`
- Create: `website/src/routes/Transcript.jsx`
- Create: `website/src/components/layout/Nav.jsx`
- Create: `website/src/components/layout/Footer.jsx`
- Create: `website/src/components/layout/Shell.jsx`
- Modify: `website/src/App.jsx`

- [ ] **Step 1: Write route stubs**

Create `website/src/routes/Landing.jsx`:

```jsx
import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center text-center px-6">
      <h1 className="font-serif text-6xl md:text-8xl leading-tight max-w-4xl">
        Catching the Fall
      </h1>
      <p className="mt-6 text-xl text-muted max-w-2xl">
        Why children drop out of vaccination in Nigeria — and what to do about it.
      </p>
      <Link
        to="/story"
        className="mt-12 inline-flex items-center gap-2 px-8 py-4 bg-saffron text-abyss font-semibold rounded-full hover:bg-saffron/90 transition"
      >
        Begin the story →
      </Link>
    </main>
  );
}
```

Create `website/src/routes/Story.jsx`:

```jsx
export default function Story() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <p className="text-muted">Story scaffold — Acts I–V built in Phase 2 and 3.</p>
    </main>
  );
}
```

Create `website/src/routes/Policy.jsx`:

```jsx
export default function Policy() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="font-serif text-4xl">Policy Dashboard</h1>
      <p className="text-muted mt-2">Scaffold — built out in Task 10+.</p>
    </main>
  );
}
```

Create `website/src/routes/Simulation.jsx`:

```jsx
export default function Simulation() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="font-serif text-4xl">Simulation</h1>
      <p className="text-muted mt-2">Scaffold — built out in Phase 4.</p>
    </main>
  );
}
```

Create `website/src/routes/Explorer.jsx`:

```jsx
export default function Explorer() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="font-serif text-4xl">Explorer</h1>
      <p className="text-muted mt-2">Scaffold — tabs built out in Phase 2.</p>
    </main>
  );
}
```

Create `website/src/routes/Methods.jsx`:

```jsx
export default function Methods() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="font-serif text-4xl">Methods</h1>
      <p className="text-muted mt-2">TRIPOD+AI methods page scaffold.</p>
    </main>
  );
}
```

Create `website/src/routes/Transcript.jsx`:

```jsx
export default function Transcript() {
  return (
    <main className="min-h-screen p-8 max-w-3xl mx-auto">
      <h1 className="font-serif text-4xl">Story Transcript</h1>
      <p className="text-muted mt-2">Text-only accessible alternative — built in Phase 4.</p>
    </main>
  );
}
```

- [ ] **Step 2: Create Nav, Footer, Shell**

Create `website/src/components/layout/Nav.jsx`:

```jsx
import { Link, NavLink } from 'react-router-dom';

const navItems = [
  { to: '/story', label: 'Story' },
  { to: '/policy', label: 'Policy' },
  { to: '/simulation', label: 'Simulation' },
  { to: '/explorer', label: 'Explorer' },
];

export default function Nav() {
  return (
    <nav className="fixed top-0 inset-x-0 z-50 bg-abyss/70 backdrop-blur-md border-b border-white/5">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        <Link to="/" className="font-serif text-xl">Catching the Fall</Link>
        <ul className="flex items-center gap-6 text-sm">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  isActive ? 'text-saffron' : 'text-muted hover:text-moonlight transition'
                }
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
```

Create `website/src/components/layout/Footer.jsx`:

```jsx
export default function Footer() {
  return (
    <footer className="border-t border-white/5 py-8 px-6 text-sm text-muted">
      <div className="max-w-7xl mx-auto flex flex-wrap gap-4 justify-between">
        <div>
          University of Warwick · Warwick Applied Health · 2026
        </div>
        <div className="flex gap-6">
          <a href="/dropout/explorer/methods" className="hover:text-moonlight">Methods</a>
          <a href="https://github.com/olatechie/dropout" className="hover:text-moonlight" target="_blank" rel="noreferrer">Code</a>
          <a href="/dropout/story/transcript" className="hover:text-moonlight">Transcript</a>
        </div>
      </div>
    </footer>
  );
}
```

Create `website/src/components/layout/Shell.jsx`:

```jsx
import Nav from './Nav.jsx';
import Footer from './Footer.jsx';

export default function Shell({ children, showChrome = true }) {
  return (
    <div className="min-h-screen flex flex-col">
      {showChrome && <Nav />}
      <div className={showChrome ? 'pt-16 flex-1' : 'flex-1'}>{children}</div>
      {showChrome && <Footer />}
    </div>
  );
}
```

- [ ] **Step 3: Wire router with lazy routes**

Replace `website/src/App.jsx`:

```jsx
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
```

- [ ] **Step 4: Verify and commit**

Run: `cd website && npm run dev`
Expected: all 7 routes navigable, nav highlights active, landing page CTA works.

```bash
git add website/
git commit -m "feat(web): add 7 routes + nav/footer shell with lazy Story/Simulation"
```

---

### Task 3: Data preparation script — pipeline outputs to tidy JSON

**Files:**
- Create: `website/scripts/prepare_website_data.py`

- [ ] **Step 1: Write script**

Create `website/scripts/prepare_website_data.py`:

```python
#!/usr/bin/env python3
"""Convert dropout pipeline outputs into tidy JSON for the website.

Reads from outputs/stage1/, outputs/stage3_v2/, outputs/validation/ and writes
optimised JSON files to website/public/data/.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
STAGE1 = REPO / "outputs" / "stage1"
STAGE3 = REPO / "outputs" / "stage3_v2"
VALID = REPO / "outputs" / "validation"
OUT = REPO / "website" / "public" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def round_floats(obj, ndigits: int = 4):
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(obj, ndigits)
    if isinstance(obj, dict):
        return {k: round_floats(v, ndigits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, ndigits) for v in obj]
    return obj


def write_json(name: str, data) -> None:
    path = OUT / f"{name}.json"
    with open(path, "w") as f:
        json.dump(round_floats(data), f, separators=(",", ":"))
    size_kb = path.stat().st_size / 1024
    print(f"  {name}.json ({size_kb:.1f} KB)")


def prepare_cascade():
    df = pd.read_csv(STAGE1 / "cascade_metrics.csv")
    write_json("cascade", df.to_dict(orient="records"))


def prepare_shap():
    with open(STAGE1 / "xgb_results_summary.json") as f:
        xgb = json.load(f)
    summary = {
        model: {
            "andersen_domains": xgb[model].get("andersen_domains", {}),
            "metrics": {k: v for k, v in xgb[model].get("metrics", {}).items()
                        if not isinstance(v, list) or len(v) <= 10},
            "delong": xgb[model].get("delong"),
            "prevalence": xgb[model].get("prevalence"),
            "n": xgb[model].get("n"),
        }
        for model in ["t1", "t2", "full"]
        if model in xgb
    }
    write_json("shap_summary", summary)


def prepare_scenarios():
    df = pd.read_csv(STAGE3 / "microsim_results.csv")
    scenarios = []
    for _, row in df.iterrows():
        scenarios.append({
            "id": row["scenario"],
            "dtp3_mean": float(row["dtp3_mean"]),
            "dtp3_ci_low": float(row["dtp3_ci_low"]),
            "dtp3_ci_high": float(row["dtp3_ci_high"]),
            "cost_per_child_mean": float(row["cost_per_child_mean"]),
            "cost_per_child_ci_low": float(row.get("cost_per_child_ci_low", row["cost_per_child_mean"])),
            "cost_per_child_ci_high": float(row.get("cost_per_child_ci_high", row["cost_per_child_mean"])),
            "concentration_index": float(row.get("concentration_index", 0)),
            "wealth_gap": float(row.get("wealth_gap", 0)),
            "slope_index": float(row.get("slope_index", 0)),
        })
    write_json("scenarios", scenarios)


def prepare_icer():
    df = pd.read_csv(STAGE3 / "icer_distribution.csv")
    write_json("icer", df.to_dict(orient="records"))


def prepare_ceac():
    df = pd.read_csv(STAGE3 / "ceac_data.csv")
    write_json("ceac", df.to_dict(orient="records"))


def prepare_psa_summary():
    """PSA point cloud for CE-plane, thinned to 250 per scenario."""
    df = pd.read_csv(STAGE3 / "microsim_psa.csv")
    out = []
    for scenario, sub in df.groupby("scenario"):
        thinned = sub.sample(n=min(250, len(sub)), random_state=42)
        for _, row in thinned.iterrows():
            out.append({
                "scenario": scenario,
                "dtp3_rate": float(row["dtp3_rate"]),
                "cost_per_child": float(row["cost_per_child"]),
                "concentration_index": float(row.get("concentration_index", 0)),
            })
    write_json("psa_summary", out)


def prepare_validation():
    vdata = {}
    internal_path = VALID / "internal_calibration.json"
    if internal_path.exists():
        with open(internal_path) as f:
            vdata["internal"] = json.load(f)
    for csv in VALID.glob("subgroup_*.csv"):
        key = csv.stem.replace("subgroup_", "")
        vdata.setdefault("subgroups", {})[key] = pd.read_csv(csv).to_dict(orient="records")
    write_json("validation", vdata)


def prepare_cohort_sample():
    """Anonymised sample of 100 trajectories for Act II click vignettes."""
    traj = pd.read_csv(REPO / "data" / "processed" / "trajectory_dataset.csv")
    sample = traj.sample(n=min(100, len(traj)), random_state=42)[
        ["child_id", "dose_step", "action", "reward", "weight"]
    ].copy()
    sample["child_id"] = [f"C{i:04d}" for i in range(len(sample))]
    out = []
    for _, row in sample.iterrows():
        out.append({
            "id": row["child_id"],
            "dose_step": int(row["dose_step"]),
            "action": int(row["action"]),
            "reward": float(row["reward"]),
            "weight": round(float(row["weight"]), 3),
        })
    write_json("cohort_sample", out)


def main():
    print(f"Writing data to: {OUT}")
    prepare_cascade()
    prepare_shap()
    prepare_scenarios()
    prepare_icer()
    prepare_ceac()
    prepare_psa_summary()
    prepare_validation()
    prepare_cohort_sample()
    print("Done.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run**

```bash
python website/scripts/prepare_website_data.py
```

Expected: prints file sizes for each JSON written to `website/public/data/`.

- [ ] **Step 3: Verify outputs**

```bash
ls -la website/public/data/
```

Expected files: `cascade.json`, `shap_summary.json`, `scenarios.json`, `icer.json`, `ceac.json`, `psa_summary.json`, `validation.json`, `cohort_sample.json`.

- [ ] **Step 4: Commit**

```bash
git add website/scripts/prepare_website_data.py website/public/data/
git commit -m "feat(web): add data preparation script — pipeline outputs to tidy JSON"
```

---

### Task 4: Scenario cube precompute script

**Files:**
- Create: `website/scripts/precompute_scenarios.py`

- [ ] **Step 1: Write script**

Create `website/scripts/precompute_scenarios.py`:

```python
#!/usr/bin/env python3
"""Precompute a scenario cube for client-side interpolation.

Grid: 5 budgets × 5 targeting rules × 3 SMS RRR × 3 CHW RRR = 225 scenarios.
Each runs 100 bootstrap iterations. Output: scenario_cube.json.
"""

from __future__ import annotations

import json
import sys
import warnings
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from dropout_rl.microsim import run_scenario
from dropout_rl.transitions import load_t1, load_t2
from dropout_rl import config as cfg
from dropout_rl import interventions as iv
from dropout_rl import costs as cst

warnings.filterwarnings("ignore")

OUT = REPO / "website" / "public" / "data"
OUT.mkdir(parents=True, exist_ok=True)

BUDGETS = [250_000_000, 500_000_000, 750_000_000, 1_000_000_000, 1_500_000_000]
TARGETING_RULES = [
    "uniform_sms",
    "uniform_chw",
    "top30_risk",
    "top10_incentive",
    "rl_optimised",
]
SMS_RRR_LEVELS = [0.05, 0.10, 0.15]
CHW_RRR_LEVELS = [0.15, 0.20, 0.25]
N_BOOTSTRAP = 100
N_POP = 5000


def make_policy(rule: str, t1_model):
    def uniform_sms(X, idx):
        return np.ones(len(X), dtype=np.int64)

    def uniform_chw(X, idx):
        return np.full(len(X), 2, dtype=np.int64)

    def top30_risk(X, idx):
        risk = t1_model.predict_dropout(X)
        thr = np.percentile(risk, 70)
        return np.where(risk >= thr, 2, 1).astype(np.int64)

    def top10_incentive(X, idx):
        risk = t1_model.predict_dropout(X)
        thr = np.percentile(risk, 90)
        return np.where(risk >= thr, 2, 1).astype(np.int64)

    def rl_optimised(X, idx):
        import joblib
        path = REPO / "outputs" / "stage2_v2" / "selected_policy.joblib"
        if not path.exists():
            return top30_risk(X, idx)
        policy = joblib.load(path)
        return policy.predict_action(X)

    return {
        "uniform_sms": uniform_sms,
        "uniform_chw": uniform_chw,
        "top30_risk": top30_risk,
        "top10_incentive": top10_incentive,
        "rl_optimised": rl_optimised,
    }[rule]


def patch_priors(sms_rrr: float, chw_rrr: float):
    """Replace the central RRR for a1 and a2 with fixed values for this grid point."""
    orig_rrr = dict(cfg.RRR_RANGES)
    cfg.RRR_RANGES[1] = (sms_rrr, sms_rrr * 0.9, sms_rrr * 1.1)
    cfg.RRR_RANGES[2] = (chw_rrr, chw_rrr * 0.9, chw_rrr * 1.1)
    return orig_rrr


def restore_priors(orig):
    cfg.RRR_RANGES.clear()
    cfg.RRR_RANGES.update(orig)


def main():
    analytic = pd.read_parquet(REPO / "data" / "processed" / "analytic_dtp1_received.parquet")
    t1 = load_t1()
    t2 = load_t2()
    total = len(BUDGETS) * len(TARGETING_RULES) * len(SMS_RRR_LEVELS) * len(CHW_RRR_LEVELS)
    print(f"Precomputing {total} grid points × {N_BOOTSTRAP} bootstraps × {N_POP} pop...")

    results = []
    i = 0
    for budget, rule, sms, chw in product(BUDGETS, TARGETING_RULES, SMS_RRR_LEVELS, CHW_RRR_LEVELS):
        i += 1
        print(f"  [{i}/{total}] budget={budget/1e6:.0f}M, rule={rule}, sms={sms}, chw={chw}")
        orig = patch_priors(sms, chw)
        try:
            policy = make_policy(rule, t1)
            res = run_scenario(
                name=f"g_{i}",
                policy_fn_t1=policy,
                policy_fn_t2=policy,
                analytic_df=analytic,
                t1_model=t1,
                t2_model=t2,
                n_pop=N_POP,
                n_bootstrap=N_BOOTSTRAP,
                cluster_bootstrap=True,
                psa=True,
                seed=42,
                is_status_quo=False,
                feature_cols=t1.feature_names,
            )
            results.append({
                "budget": int(budget),
                "rule": rule,
                "sms_rrr": float(sms),
                "chw_rrr": float(chw),
                "dtp3_mean": float(res.dtp3_rate.mean()),
                "dtp3_ci_low": float(np.percentile(res.dtp3_rate, 2.5)),
                "dtp3_ci_high": float(np.percentile(res.dtp3_rate, 97.5)),
                "cost_per_child": float(res.cost_per_child.mean()),
                "concentration_index": float(res.concentration_index.mean()),
                "wealth_gap": float(res.wealth_gap.mean()),
            })
        finally:
            restore_priors(orig)

    out_path = OUT / "scenario_cube.json"
    with open(out_path, "w") as f:
        json.dump({
            "grid": {
                "budgets": BUDGETS,
                "rules": TARGETING_RULES,
                "sms_rrr": SMS_RRR_LEVELS,
                "chw_rrr": CHW_RRR_LEVELS,
            },
            "points": results,
        }, f, separators=(",", ":"))
    size_kb = out_path.stat().st_size / 1024
    print(f"Wrote scenario_cube.json ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run (long-running, ~2-4 hours for 225 scenarios)**

```bash
python website/scripts/precompute_scenarios.py
```

Use `nohup ... &` or tmux; monitor progress via terminal output.

- [ ] **Step 3: Verify output**

```bash
ls -la website/public/data/scenario_cube.json
```

Expected: file exists, 500KB-2MB unzipped.

- [ ] **Step 4: Commit**

```bash
git add website/scripts/precompute_scenarios.py website/public/data/scenario_cube.json
git commit -m "feat(web): add scenario cube precompute (225 grid points) for interpolation"
```

---

### Task 5: Data loader + cache utility (TDD)

**Files:**
- Create: `website/src/lib/dataLoader.js`
- Create: `website/src/lib/dataLoader.test.js`

- [ ] **Step 1: Write failing tests**

Create `website/src/lib/dataLoader.test.js`:

```js
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { loadData, clearCache } from './dataLoader.js';

describe('dataLoader', () => {
  beforeEach(() => {
    clearCache();
    global.fetch = vi.fn();
  });

  it('fetches JSON from /data/<name>.json', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ foo: 1 }),
    });
    const data = await loadData('cascade');
    expect(fetch).toHaveBeenCalledWith('/dropout/data/cascade.json');
    expect(data).toEqual({ foo: 1 });
  });

  it('caches by name — second call does not refetch', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ cached: true }),
    });
    await loadData('cascade');
    await loadData('cascade');
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('throws on fetch error', async () => {
    fetch.mockResolvedValueOnce({ ok: false, status: 404 });
    await expect(loadData('missing')).rejects.toThrow();
  });

  it('clearCache allows re-fetch', async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ n: 1 }),
    });
    await loadData('x');
    clearCache();
    await loadData('x');
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd website && npx vitest run src/lib/dataLoader.test.js`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Write implementation**

Create `website/src/lib/dataLoader.js`:

```js
const BASE = import.meta.env.BASE_URL || '/';
const cache = new Map();

export async function loadData(name) {
  if (cache.has(name)) return cache.get(name);
  const url = `${BASE}data/${name}.json`.replace(/\/+/g, '/');
  const promise = fetch(url).then((r) => {
    if (!r.ok) throw new Error(`Failed to load ${name}: ${r.status}`);
    return r.json();
  });
  cache.set(name, promise);
  try {
    return await promise;
  } catch (err) {
    cache.delete(name);
    throw err;
  }
}

export function clearCache() {
  cache.clear();
}
```

- [ ] **Step 4: Run tests**

Run: `cd website && npx vitest run src/lib/dataLoader.test.js`
Expected: 4 passing.

- [ ] **Step 5: Commit**

```bash
git add website/src/lib/dataLoader.js website/src/lib/dataLoader.test.js
git commit -m "feat(web): add dataLoader with per-name in-memory cache (TDD)"
```

---

### Task 6: Scenario interpolation engine (TDD)

**Files:**
- Create: `website/src/lib/interp.js`
- Create: `website/src/lib/interp.test.js`

- [ ] **Step 1: Write failing tests**

Create `website/src/lib/interp.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { buildCubeIndex, interpolateScenario } from './interp.js';

const fixture = {
  grid: {
    budgets: [250_000_000, 500_000_000],
    rules: ['uniform_sms', 'top30_risk'],
    sms_rrr: [0.05, 0.15],
    chw_rrr: [0.15, 0.25],
  },
  points: [
    // uniform_sms corners
    { budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.15, dtp3_mean: 0.80, cost_per_child: 100 },
    { budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.25, dtp3_mean: 0.81, cost_per_child: 100 },
    { budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.15, chw_rrr: 0.15, dtp3_mean: 0.84, cost_per_child: 100 },
    { budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.15, chw_rrr: 0.25, dtp3_mean: 0.85, cost_per_child: 100 },
    { budget: 500_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.15, dtp3_mean: 0.82, cost_per_child: 100 },
    { budget: 500_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.25, dtp3_mean: 0.83, cost_per_child: 100 },
    { budget: 500_000_000, rule: 'uniform_sms', sms_rrr: 0.15, chw_rrr: 0.15, dtp3_mean: 0.86, cost_per_child: 100 },
    { budget: 500_000_000, rule: 'uniform_sms', sms_rrr: 0.15, chw_rrr: 0.25, dtp3_mean: 0.87, cost_per_child: 100 },
  ],
};

describe('interp', () => {
  const cube = buildCubeIndex(fixture);

  it('exact grid point returns stored value', () => {
    const r = interpolateScenario(cube, {
      budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.15,
    });
    expect(r.dtp3_mean).toBeCloseTo(0.80, 4);
  });

  it('midpoint interpolates linearly', () => {
    const r = interpolateScenario(cube, {
      budget: 375_000_000, rule: 'uniform_sms', sms_rrr: 0.10, chw_rrr: 0.20,
    });
    // Mean of 8 corners: (0.80+0.81+0.84+0.85+0.82+0.83+0.86+0.87) / 8 = 0.835
    expect(r.dtp3_mean).toBeCloseTo(0.835, 3);
  });

  it('clamps out-of-range budget to nearest edge', () => {
    const r = interpolateScenario(cube, {
      budget: 100_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.15,
    });
    expect(r.dtp3_mean).toBeCloseTo(0.80, 4);
  });

  it('throws for unknown rule', () => {
    expect(() =>
      interpolateScenario(cube, {
        budget: 250_000_000, rule: 'unknown', sms_rrr: 0.05, chw_rrr: 0.15,
      })
    ).toThrow(/unknown/i);
  });
});
```

- [ ] **Step 2: Run test to verify failure**

Run: `cd website && npx vitest run src/lib/interp.test.js`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Write implementation**

Create `website/src/lib/interp.js`:

```js
/**
 * Build an index keyed by rule, then a 3D grid over (budget, sms_rrr, chw_rrr).
 */
export function buildCubeIndex(cube) {
  const { grid, points } = cube;
  const byRule = {};
  for (const rule of grid.rules) {
    byRule[rule] = {};
    for (const b of grid.budgets) {
      byRule[rule][b] = {};
      for (const s of grid.sms_rrr) {
        byRule[rule][b][s] = {};
        for (const c of grid.chw_rrr) {
          byRule[rule][b][s][c] = null;
        }
      }
    }
  }
  for (const p of points) {
    if (byRule[p.rule]?.[p.budget]?.[p.sms_rrr]?.[p.chw_rrr] !== undefined) {
      byRule[p.rule][p.budget][p.sms_rrr][p.chw_rrr] = p;
    }
  }
  return { grid, byRule };
}

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function findBracket(sorted, v) {
  const clamped = clamp(v, sorted[0], sorted[sorted.length - 1]);
  for (let i = 0; i < sorted.length - 1; i++) {
    if (clamped >= sorted[i] && clamped <= sorted[i + 1]) {
      const t = (clamped - sorted[i]) / (sorted[i + 1] - sorted[i]);
      return [sorted[i], sorted[i + 1], t];
    }
  }
  return [sorted[0], sorted[0], 0];
}

const FIELDS = [
  'dtp3_mean', 'dtp3_ci_low', 'dtp3_ci_high',
  'cost_per_child', 'concentration_index', 'wealth_gap',
];

/**
 * Trilinear interpolation over (budget, sms_rrr, chw_rrr) within a targeting rule.
 */
export function interpolateScenario(cube, { budget, rule, sms_rrr, chw_rrr }) {
  const { grid, byRule } = cube;
  if (!byRule[rule]) {
    throw new Error(`Unknown targeting rule: ${rule}`);
  }

  const [b0, b1, tb] = findBracket(grid.budgets, budget);
  const [s0, s1, ts] = findBracket(grid.sms_rrr, sms_rrr);
  const [c0, c1, tc] = findBracket(grid.chw_rrr, chw_rrr);

  const corners = [];
  for (const b of [b0, b1]) {
    for (const s of [s0, s1]) {
      for (const c of [c0, c1]) {
        const p = byRule[rule][b]?.[s]?.[c];
        if (!p) throw new Error(`Missing grid point: ${rule} b=${b} s=${s} c=${c}`);
        corners.push(p);
      }
    }
  }

  // Corner order: (b0,s0,c0)(b0,s0,c1)(b0,s1,c0)(b0,s1,c1)(b1,s0,c0)(b1,s0,c1)(b1,s1,c0)(b1,s1,c1)
  const lerp = (a, b, t) => a * (1 - t) + b * t;

  const out = {};
  for (const field of FIELDS) {
    const v = corners.map((p) => p[field] ?? 0);
    const cxy00 = lerp(v[0], v[4], tb);
    const cxy01 = lerp(v[1], v[5], tb);
    const cxy10 = lerp(v[2], v[6], tb);
    const cxy11 = lerp(v[3], v[7], tb);
    const cy0 = lerp(cxy00, cxy10, ts);
    const cy1 = lerp(cxy01, cxy11, ts);
    out[field] = lerp(cy0, cy1, tc);
  }
  out.budget = budget;
  out.rule = rule;
  out.sms_rrr = sms_rrr;
  out.chw_rrr = chw_rrr;
  return out;
}
```

- [ ] **Step 4: Run tests**

Run: `cd website && npx vitest run src/lib/interp.test.js`
Expected: 4 passing.

- [ ] **Step 5: Commit**

```bash
git add website/src/lib/interp.js website/src/lib/interp.test.js
git commit -m "feat(web): trilinear scenario interpolation with unit tests"
```

---

### Task 7: Zustand stores (story, scenario)

**Files:**
- Create: `website/src/state/story.js`
- Create: `website/src/state/scenario.js`
- Create: `website/src/state/scenario.test.js`

- [ ] **Step 1: Write failing tests**

Create `website/src/state/scenario.test.js`:

```js
import { describe, it, expect, beforeEach } from 'vitest';
import { useScenarioStore } from './scenario.js';

describe('scenario store', () => {
  beforeEach(() => {
    useScenarioStore.setState({
      budget: 500_000_000,
      rule: 'top30_risk',
      sms_rrr: 0.10,
      chw_rrr: 0.20,
      interventions: { a0: true, a1: true, a2: true, a3: false, a4: false },
    });
  });

  it('has sensible defaults', () => {
    const s = useScenarioStore.getState();
    expect(s.budget).toBe(500_000_000);
    expect(s.rule).toBe('top30_risk');
  });

  it('setBudget updates budget', () => {
    useScenarioStore.getState().setBudget(750_000_000);
    expect(useScenarioStore.getState().budget).toBe(750_000_000);
  });

  it('toggleIntervention flips boolean', () => {
    useScenarioStore.getState().toggleIntervention('a3');
    expect(useScenarioStore.getState().interventions.a3).toBe(true);
    useScenarioStore.getState().toggleIntervention('a3');
    expect(useScenarioStore.getState().interventions.a3).toBe(false);
  });

  it('encodeToURL serializes state', () => {
    const s = useScenarioStore.getState();
    const url = s.encodeToURL();
    expect(url).toContain('budget=500');
    expect(url).toContain('rule=top30_risk');
  });
});
```

- [ ] **Step 2: Run test**

Run: `cd website && npx vitest run src/state/scenario.test.js`
Expected: FAIL.

- [ ] **Step 3: Write scenario store**

Create `website/src/state/scenario.js`:

```js
import { create } from 'zustand';

export const useScenarioStore = create((set, get) => ({
  budget: 500_000_000,
  rule: 'top30_risk',
  sms_rrr: 0.10,
  chw_rrr: 0.20,
  interventions: { a0: true, a1: true, a2: true, a3: false, a4: false },

  setBudget: (v) => set({ budget: v }),
  setRule: (v) => set({ rule: v }),
  setSmsRrr: (v) => set({ sms_rrr: v }),
  setChwRrr: (v) => set({ chw_rrr: v }),
  toggleIntervention: (key) =>
    set((s) => ({ interventions: { ...s.interventions, [key]: !s.interventions[key] } })),
  reset: () =>
    set({
      budget: 500_000_000,
      rule: 'top30_risk',
      sms_rrr: 0.10,
      chw_rrr: 0.20,
      interventions: { a0: true, a1: true, a2: true, a3: false, a4: false },
    }),

  encodeToURL: () => {
    const { budget, rule, sms_rrr, chw_rrr, interventions } = get();
    const params = new URLSearchParams({
      budget: `${budget / 1e6}M`,
      rule,
      sms: sms_rrr.toFixed(2),
      chw: chw_rrr.toFixed(2),
      ivs: Object.keys(interventions).filter((k) => interventions[k]).join(','),
    });
    return params.toString();
  },

  decodeFromURL: (searchString) => {
    const params = new URLSearchParams(searchString);
    const updates = {};
    const b = params.get('budget');
    if (b) updates.budget = parseInt(b, 10) * 1e6;
    const rule = params.get('rule');
    if (rule) updates.rule = rule;
    const sms = params.get('sms');
    if (sms) updates.sms_rrr = parseFloat(sms);
    const chw = params.get('chw');
    if (chw) updates.chw_rrr = parseFloat(chw);
    const ivs = params.get('ivs');
    if (ivs) {
      updates.interventions = { a0: false, a1: false, a2: false, a3: false, a4: false };
      ivs.split(',').forEach((k) => { updates.interventions[k] = true; });
    }
    set(updates);
  },
}));
```

Create `website/src/state/story.js`:

```js
import { create } from 'zustand';

export const useStoryStore = create((set) => ({
  currentAct: 1,             // 1..5
  actProgress: 0,            // 0..1 within current act
  audioEnabled: false,
  reducedMotion: false,

  setAct: (act) => set({ currentAct: act, actProgress: 0 }),
  setActProgress: (p) => set({ actProgress: p }),
  toggleAudio: () => set((s) => ({ audioEnabled: !s.audioEnabled })),
  setReducedMotion: (v) => set({ reducedMotion: v }),
}));
```

- [ ] **Step 4: Run tests**

Run: `cd website && npx vitest run src/state/scenario.test.js`
Expected: 4 passing.

- [ ] **Step 5: Commit**

```bash
git add website/src/state/
git commit -m "feat(web): add Zustand stores (story + scenario with URL encode/decode)"
```

---

### Task 8: Policy page MVP — scenario table + budget slider

**Files:**
- Create: `website/src/routes/Policy.jsx` (replace stub)
- Create: `website/src/components/charts/ScenarioTable.jsx`
- Create: `website/src/components/hud/BudgetSlider.jsx`
- Create: `website/src/components/shared/MetricCard.jsx`
- Create: `website/src/lib/format.js`
- Create: `website/src/lib/format.test.js`

- [ ] **Step 1: Format helpers with tests**

Create `website/src/lib/format.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { formatNaira, formatPct, formatNumber } from './format.js';

describe('format', () => {
  it('formats Naira', () => {
    expect(formatNaira(500)).toBe('₦500');
    expect(formatNaira(1500)).toBe('₦1,500');
    expect(formatNaira(500_000_000)).toBe('₦500M');
    expect(formatNaira(1_200_000_000)).toBe('₦1.2B');
  });
  it('formats percent', () => {
    expect(formatPct(0.85)).toBe('85%');
    expect(formatPct(0.8567, 1)).toBe('85.7%');
  });
  it('formats number with commas', () => {
    expect(formatNumber(3194)).toBe('3,194');
  });
});
```

Create `website/src/lib/format.js`:

```js
export function formatNaira(v) {
  if (v >= 1e9) return `₦${(v / 1e9).toFixed(v < 1e10 ? 1 : 0)}B`;
  if (v >= 1e6) return `₦${(v / 1e6).toFixed(0)}M`;
  if (v >= 1e3) return `₦${Math.round(v).toLocaleString('en-NG')}`;
  return `₦${Math.round(v)}`;
}

export function formatPct(v, digits = 0) {
  return `${(v * 100).toFixed(digits)}%`;
}

export function formatNumber(v) {
  return Math.round(v).toLocaleString('en-NG');
}
```

Run: `cd website && npx vitest run src/lib/format.test.js` → 3 passing.

- [ ] **Step 2: MetricCard component**

Create `website/src/components/shared/MetricCard.jsx`:

```jsx
export default function MetricCard({ label, value, sublabel, tone = 'default' }) {
  const tones = {
    default: 'bg-dusk border-white/10',
    positive: 'bg-dusk border-verdigris/50',
    warning: 'bg-dusk border-saffron/50',
    negative: 'bg-dusk border-terracotta/50',
  };
  return (
    <div className={`rounded-2xl border p-6 ${tones[tone]}`}>
      <div className="text-xs uppercase tracking-wider text-muted">{label}</div>
      <div className="mt-2 font-serif text-4xl tabular-nums">{value}</div>
      {sublabel && <div className="mt-1 text-sm text-muted">{sublabel}</div>}
    </div>
  );
}
```

- [ ] **Step 3: BudgetSlider component**

Create `website/src/components/hud/BudgetSlider.jsx`:

```jsx
import { useScenarioStore } from '../../state/scenario.js';
import { formatNaira } from '../../lib/format.js';

export default function BudgetSlider({ min = 250_000_000, max = 1_500_000_000, step = 25_000_000 }) {
  const budget = useScenarioStore((s) => s.budget);
  const setBudget = useScenarioStore((s) => s.setBudget);

  return (
    <div>
      <div className="flex items-baseline justify-between mb-2">
        <label htmlFor="budget" className="text-sm text-muted">National annual budget</label>
        <span className="font-serif text-2xl tabular-nums">{formatNaira(budget)}</span>
      </div>
      <input
        id="budget"
        type="range"
        min={min}
        max={max}
        step={step}
        value={budget}
        onChange={(e) => setBudget(parseInt(e.target.value, 10))}
        className="w-full accent-saffron"
        aria-label="National budget"
      />
      <div className="mt-1 flex justify-between text-xs text-muted">
        <span>{formatNaira(min)}</span>
        <span>{formatNaira(max)}</span>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: ScenarioTable component**

Create `website/src/components/charts/ScenarioTable.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { loadData } from '../../lib/dataLoader.js';
import { formatNaira, formatPct } from '../../lib/format.js';

export default function ScenarioTable() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    loadData('scenarios').then(setRows);
  }, []);

  if (!rows.length) return <div className="text-muted">Loading scenarios…</div>;

  return (
    <div className="overflow-auto rounded-2xl border border-white/10">
      <table className="w-full text-sm">
        <thead className="bg-dusk">
          <tr className="text-left">
            <th className="px-4 py-3 font-medium">Scenario</th>
            <th className="px-4 py-3 font-medium tabular-nums">DTP3 (95% CI)</th>
            <th className="px-4 py-3 font-medium tabular-nums">Cost / child</th>
            <th className="px-4 py-3 font-medium tabular-nums">Concentration index</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t border-white/5 hover:bg-dusk/50">
              <td className="px-4 py-3">{r.id}</td>
              <td className="px-4 py-3 tabular-nums">
                {formatPct(r.dtp3_mean, 1)}
                <span className="text-xs text-muted ml-2">
                  ({formatPct(r.dtp3_ci_low, 1)}–{formatPct(r.dtp3_ci_high, 1)})
                </span>
              </td>
              <td className="px-4 py-3 tabular-nums">{formatNaira(r.cost_per_child_mean)}</td>
              <td className="px-4 py-3 tabular-nums">{r.concentration_index.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 5: Build Policy page**

Replace `website/src/routes/Policy.jsx`:

```jsx
import { useEffect, useState } from 'react';
import ScenarioTable from '../components/charts/ScenarioTable.jsx';
import BudgetSlider from '../components/hud/BudgetSlider.jsx';
import MetricCard from '../components/shared/MetricCard.jsx';
import { loadData } from '../lib/dataLoader.js';
import { buildCubeIndex, interpolateScenario } from '../lib/interp.js';
import { useScenarioStore } from '../state/scenario.js';
import { formatNaira, formatPct } from '../lib/format.js';

export default function Policy() {
  const [cube, setCube] = useState(null);
  const { budget, rule, sms_rrr, chw_rrr } = useScenarioStore();

  useEffect(() => {
    loadData('scenario_cube').then((raw) => setCube(buildCubeIndex(raw)));
  }, []);

  const live = cube ? interpolateScenario(cube, { budget, rule, sms_rrr, chw_rrr }) : null;

  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      <header className="mb-12">
        <h1 className="font-serif text-5xl">Policy Dashboard</h1>
        <p className="mt-3 text-muted max-w-2xl">
          Compare intervention scenarios for reducing DTP1-to-DTP3 dropout in Nigeria.
          Adjust the budget below to see how outcomes and costs shift.
        </p>
      </header>

      <section className="grid md:grid-cols-3 gap-6 mb-12">
        <MetricCard
          label="Live DTP3 completion"
          value={live ? formatPct(live.dtp3_mean, 1) : '—'}
          sublabel={live ? `CI ${formatPct(live.dtp3_ci_low, 1)}–${formatPct(live.dtp3_ci_high, 1)}` : ''}
          tone="positive"
        />
        <MetricCard
          label="Cost per child"
          value={live ? formatNaira(live.cost_per_child) : '—'}
          sublabel={`Rule: ${rule}`}
        />
        <MetricCard
          label="Concentration index"
          value={live ? live.concentration_index.toFixed(3) : '—'}
          sublabel="Wealth-related inequality"
          tone={live && live.concentration_index < 0.02 ? 'positive' : 'warning'}
        />
      </section>

      <section className="rounded-2xl border border-white/10 bg-dusk/30 p-8 mb-12">
        <h2 className="font-serif text-2xl mb-6">Adjust the budget</h2>
        <BudgetSlider />
      </section>

      <section>
        <h2 className="font-serif text-2xl mb-6">Primary scenarios</h2>
        <ScenarioTable />
      </section>
    </main>
  );
}
```

- [ ] **Step 6: Run dev + commit**

Run: `cd website && npm run dev` — open `/policy`, verify budget slider updates live cards, table loads.

```bash
git add website/src/routes/Policy.jsx website/src/components/ website/src/lib/format.js website/src/lib/format.test.js
git commit -m "feat(web): policy dashboard MVP — scenario table + live budget slider"
```

---

## Phase 2: Explorer Tabs · Story Acts I–II (Week 2)

### Task 9: Explorer tabs shell

**Files:**
- Create: `website/src/routes/Explorer.jsx` (replace)
- Create: `website/src/components/explorer/TabNav.jsx`
- Create: `website/src/components/explorer/tabs/Cascade.jsx`
- Create: `website/src/components/explorer/tabs/PredictionModels.jsx`
- Create: `website/src/components/explorer/tabs/Shap.jsx`
- Create: `website/src/components/explorer/tabs/RL.jsx`
- Create: `website/src/components/explorer/tabs/Microsim.jsx`
- Create: `website/src/components/explorer/tabs/Equity.jsx`
- Create: `website/src/components/explorer/tabs/Validation.jsx`
- Create: `website/src/components/explorer/tabs/Downloads.jsx`

- [ ] **Step 1: Tab nav**

Create `website/src/components/explorer/TabNav.jsx`:

```jsx
import { NavLink, useSearchParams } from 'react-router-dom';

const TABS = [
  { id: 'cascade', label: 'Cascade' },
  { id: 'models', label: 'Prediction models' },
  { id: 'shap', label: 'SHAP / Andersen' },
  { id: 'rl', label: 'Offline RL' },
  { id: 'microsim', label: 'Microsim' },
  { id: 'equity', label: 'Equity' },
  { id: 'validation', label: 'Validation' },
  { id: 'downloads', label: 'Downloads' },
];

export default function TabNav({ active, onChange }) {
  return (
    <div className="border-b border-white/5 mb-8 overflow-x-auto">
      <ul className="flex gap-6 min-w-max">
        {TABS.map((t) => (
          <li key={t.id}>
            <button
              onClick={() => onChange(t.id)}
              className={`py-3 text-sm border-b-2 transition ${
                active === t.id ? 'border-saffron text-moonlight' : 'border-transparent text-muted hover:text-moonlight'
              }`}
            >
              {t.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

- [ ] **Step 2: Explorer route with tab switching**

Replace `website/src/routes/Explorer.jsx`:

```jsx
import { useState } from 'react';
import TabNav from '../components/explorer/TabNav.jsx';
import Cascade from '../components/explorer/tabs/Cascade.jsx';
import PredictionModels from '../components/explorer/tabs/PredictionModels.jsx';
import Shap from '../components/explorer/tabs/Shap.jsx';
import RL from '../components/explorer/tabs/RL.jsx';
import Microsim from '../components/explorer/tabs/Microsim.jsx';
import Equity from '../components/explorer/tabs/Equity.jsx';
import Validation from '../components/explorer/tabs/Validation.jsx';
import Downloads from '../components/explorer/tabs/Downloads.jsx';

const TAB_MAP = {
  cascade: Cascade,
  models: PredictionModels,
  shap: Shap,
  rl: RL,
  microsim: Microsim,
  equity: Equity,
  validation: Validation,
  downloads: Downloads,
};

export default function Explorer() {
  const [active, setActive] = useState('cascade');
  const Active = TAB_MAP[active];
  return (
    <main className="max-w-6xl mx-auto px-6 py-12">
      <header className="mb-8">
        <h1 className="font-serif text-5xl">Explorer</h1>
        <p className="mt-3 text-muted max-w-2xl">
          Researcher-grade data from the full dropout analytical pipeline.
        </p>
      </header>
      <TabNav active={active} onChange={setActive} />
      <Active />
    </main>
  );
}
```

- [ ] **Step 3: Placeholder tab stubs**

Each tab file (`Cascade.jsx`, `PredictionModels.jsx`, ..., `Downloads.jsx`) follows the same stub pattern. Use this template and replace the label per tab:

Create `website/src/components/explorer/tabs/Cascade.jsx`:

```jsx
export default function Cascade() {
  return (
    <div className="text-muted">
      <h2 className="font-serif text-2xl text-moonlight mb-4">Immunisation cascade</h2>
      <p>Cascade metrics by zone + funnel plot + LISA map — built in Task 10.</p>
    </div>
  );
}
```

Repeat for each tab using its name: `PredictionModels.jsx`, `Shap.jsx`, `RL.jsx`, `Microsim.jsx`, `Equity.jsx`, `Validation.jsx`, `Downloads.jsx`. Each is 8 lines, same pattern, only the label differs.

- [ ] **Step 4: Verify and commit**

Run: `cd website && npm run dev` — open `/explorer`, click through 8 tabs.

```bash
git add website/src/routes/Explorer.jsx website/src/components/explorer/
git commit -m "feat(web): explorer tabs shell with 8 stub tabs"
```

---

### Task 10: Cascade tab — bar chart + zone comparison

**Files:**
- Modify: `website/src/components/explorer/tabs/Cascade.jsx`
- Create: `website/src/components/charts/CascadeChart.jsx`

- [ ] **Step 1: CascadeChart component**

Create `website/src/components/charts/CascadeChart.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import { loadData } from '../../lib/dataLoader.js';

export default function CascadeChart() {
  const [data, setData] = useState(null);

  useEffect(() => {
    loadData('cascade').then(setData);
  }, []);

  if (!data) return <div className="text-muted">Loading cascade…</div>;

  return (
    <div className="w-full h-96 rounded-2xl border border-white/10 bg-dusk/30 p-6">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A2340" />
          <XAxis dataKey="zone" stroke="#9AA3B8" style={{ fontSize: 12 }} />
          <YAxis stroke="#9AA3B8" style={{ fontSize: 12 }} label={{ value: 'Coverage %', angle: -90, position: 'insideLeft', fill: '#9AA3B8' }} />
          <Tooltip contentStyle={{ background: '#0D1220', border: '1px solid #1A2340', color: '#F4F0E6' }} />
          <Legend />
          <Bar dataKey="dtp1_pct" name="DTP1" fill="#F5B042" />
          <Bar dataKey="dtp2_pct" name="DTP2" fill="#5A7BFF" />
          <Bar dataKey="dtp3_pct" name="DTP3" fill="#47B7A0" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

- [ ] **Step 2: Update Cascade tab**

Replace `website/src/components/explorer/tabs/Cascade.jsx`:

```jsx
import CascadeChart from '../../charts/CascadeChart.jsx';
import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';
import { formatPct } from '../../../lib/format.js';

export default function Cascade() {
  const [rows, setRows] = useState([]);
  useEffect(() => { loadData('cascade').then(setRows); }, []);

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Immunisation cascade by zone</h2>
      <p className="text-muted max-w-3xl mb-8">
        DTP1, DTP2, and DTP3 coverage across Nigeria's six geopolitical zones, with WHO dropout rate. Values from the analytic sample of 3,194 children aged 12–23 months.
      </p>

      <CascadeChart />

      <table className="w-full mt-12 text-sm border border-white/10 rounded-2xl overflow-hidden">
        <thead className="bg-dusk">
          <tr className="text-left">
            <th className="px-4 py-3">Zone</th>
            <th className="px-4 py-3 tabular-nums">n</th>
            <th className="px-4 py-3 tabular-nums">DTP1</th>
            <th className="px-4 py-3 tabular-nums">DTP2</th>
            <th className="px-4 py-3 tabular-nums">DTP3</th>
            <th className="px-4 py-3 tabular-nums">WHO dropout</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.zone} className="border-t border-white/5">
              <td className="px-4 py-3">{r.zone}</td>
              <td className="px-4 py-3 tabular-nums">{r.n}</td>
              <td className="px-4 py-3 tabular-nums">{formatPct(r.dtp1_pct / 100, 1)}</td>
              <td className="px-4 py-3 tabular-nums">{formatPct(r.dtp2_pct / 100, 1)}</td>
              <td className="px-4 py-3 tabular-nums">{formatPct(r.dtp3_pct / 100, 1)}</td>
              <td className="px-4 py-3 tabular-nums">{formatPct(r.who_dropout / 100, 1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add website/src/components/
git commit -m "feat(web): cascade tab with bar chart + zone table"
```

---

### Task 11: Prediction models + SHAP + RL + Microsim + Equity + Validation tabs

Build remaining Explorer tabs. Each follows the same pattern: load JSON from `loadData()`, render with Recharts or a custom chart, include a data table.

**Files (7 tab files):**
- Modify: `website/src/components/explorer/tabs/PredictionModels.jsx`
- Modify: `website/src/components/explorer/tabs/Shap.jsx`
- Modify: `website/src/components/explorer/tabs/RL.jsx`
- Modify: `website/src/components/explorer/tabs/Microsim.jsx`
- Modify: `website/src/components/explorer/tabs/Equity.jsx`
- Modify: `website/src/components/explorer/tabs/Validation.jsx`
- Modify: `website/src/components/explorer/tabs/Downloads.jsx`

- [ ] **Step 1: PredictionModels tab**

Replace `website/src/components/explorer/tabs/PredictionModels.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';

export default function PredictionModels() {
  const [data, setData] = useState(null);
  useEffect(() => { loadData('shap_summary').then(setData); }, []);
  if (!data) return <div className="text-muted">Loading…</div>;

  const rows = Object.entries(data).map(([model, d]) => ({ model, ...d }));

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Transition-specific prediction models</h2>
      <p className="text-muted max-w-3xl mb-8">
        Three XGBoost models predict dropout at each cascade transition. Isotonic recalibration applied post-hoc. DeLong test compares against logistic regression baseline.
      </p>
      <div className="grid md:grid-cols-3 gap-6">
        {rows.map((r) => (
          <div key={r.model} className="rounded-2xl border border-white/10 bg-dusk/30 p-6">
            <div className="font-mono text-xs text-muted uppercase">{r.model}</div>
            <div className="mt-2 font-serif text-3xl">{r.metrics?.auc_roc ? r.metrics.auc_roc.toFixed(3) : '—'}</div>
            <div className="text-sm text-muted mt-1">AUC-ROC</div>
            <dl className="mt-4 text-sm space-y-1">
              <div className="flex justify-between"><dt className="text-muted">AUC-PR</dt><dd className="tabular-nums">{r.metrics?.auc_pr?.toFixed(3) ?? '—'}</dd></div>
              <div className="flex justify-between"><dt className="text-muted">Prevalence</dt><dd className="tabular-nums">{r.prevalence ? (r.prevalence * 100).toFixed(1) + '%' : '—'}</dd></div>
              <div className="flex justify-between"><dt className="text-muted">N</dt><dd className="tabular-nums">{r.n ?? '—'}</dd></div>
              <div className="flex justify-between"><dt className="text-muted">DeLong p</dt><dd className="tabular-nums">{r.delong?.p ? r.delong.p.toExponential(1) : '—'}</dd></div>
            </dl>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: SHAP tab**

Replace `website/src/components/explorer/tabs/Shap.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts';
import { loadData } from '../../../lib/dataLoader.js';

export default function Shap() {
  const [data, setData] = useState(null);
  useEffect(() => { loadData('shap_summary').then(setData); }, []);
  if (!data) return <div className="text-muted">Loading…</div>;

  const DOMAINS = ['Predisposing', 'Enabling', 'Need', 'Dynamic'];
  const chart = DOMAINS.map((d) => ({
    domain: d,
    T1: data.t1?.andersen_domains?.[d] ?? 0,
    T2: data.t2?.andersen_domains?.[d] ?? 0,
    Full: data.full?.andersen_domains?.[d] ?? 0,
  }));

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">SHAP · Andersen domain decomposition</h2>
      <p className="text-muted max-w-3xl mb-8">
        Mean absolute SHAP by Andersen domain for each transition-specific model. Dynamic temporal features dominate all three models, challenging the original hypothesis.
      </p>
      <div className="w-full h-96 rounded-2xl border border-white/10 bg-dusk/30 p-6">
        <ResponsiveContainer>
          <BarChart data={chart}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1A2340" />
            <XAxis dataKey="domain" stroke="#9AA3B8" style={{ fontSize: 12 }} />
            <YAxis stroke="#9AA3B8" style={{ fontSize: 12 }} label={{ value: 'Mean |SHAP|', angle: -90, position: 'insideLeft', fill: '#9AA3B8' }} />
            <Tooltip contentStyle={{ background: '#0D1220', border: '1px solid #1A2340', color: '#F4F0E6' }} />
            <Legend />
            <Bar dataKey="T1" fill="#F5B042" />
            <Bar dataKey="T2" fill="#5A7BFF" />
            <Bar dataKey="Full" fill="#47B7A0" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: RL tab**

Replace `website/src/components/explorer/tabs/RL.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';

export default function RL() {
  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Offline reinforcement learning</h2>
      <p className="text-muted max-w-3xl mb-8">
        Three offline RL algorithms (CQL, IQL, BCQ) trained on the same 3-action trajectory dataset. IQL selected as winner on FQE, with OOD frequency of 0%.
      </p>
      <div className="grid md:grid-cols-3 gap-6">
        {[
          { alg: 'CQL', fqe: 0.700, wis: '—', ood: '0.0%' },
          { alg: 'IQL (winner)', fqe: 0.872, wis: '—', ood: '0.0%' },
          { alg: 'BCQ', fqe: 0.610, wis: '—', ood: '0.0%' },
        ].map((r) => (
          <div key={r.alg} className={`rounded-2xl border p-6 ${r.alg.includes('winner') ? 'border-saffron/70 bg-saffron/5' : 'border-white/10 bg-dusk/30'}`}>
            <div className="font-mono text-xs uppercase text-muted">{r.alg}</div>
            <div className="mt-2 font-serif text-3xl tabular-nums">{r.fqe.toFixed(3)}</div>
            <div className="text-sm text-muted">FQE policy value</div>
            <div className="mt-4 text-sm">OOD frequency: <span className="tabular-nums">{r.ood}</span></div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Microsim tab**

Replace `website/src/components/explorer/tabs/Microsim.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';
import { formatNaira, formatPct } from '../../../lib/format.js';

export default function Microsim() {
  const [scenarios, setScenarios] = useState([]);
  useEffect(() => { loadData('scenarios').then(setScenarios); }, []);

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Microsimulation — 6 primary scenarios</h2>
      <p className="text-muted max-w-3xl mb-8">
        10,000 synthetic children × 1,000 bootstrap iterations × PSA on RRR and costs × cluster-bootstrap on PSUs. All values reflect full uncertainty propagation.
      </p>
      <div className="rounded-2xl border border-white/10 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-dusk">
            <tr className="text-left">
              <th className="px-4 py-3">Scenario</th>
              <th className="px-4 py-3 tabular-nums">DTP3</th>
              <th className="px-4 py-3 tabular-nums">Cost/child</th>
              <th className="px-4 py-3 tabular-nums">Concentration index</th>
              <th className="px-4 py-3 tabular-nums">Wealth gap</th>
            </tr>
          </thead>
          <tbody>
            {scenarios.map((s) => (
              <tr key={s.id} className="border-t border-white/5">
                <td className="px-4 py-3">{s.id}</td>
                <td className="px-4 py-3 tabular-nums">{formatPct(s.dtp3_mean, 1)}</td>
                <td className="px-4 py-3 tabular-nums">{formatNaira(s.cost_per_child_mean)}</td>
                <td className="px-4 py-3 tabular-nums">{s.concentration_index.toFixed(3)}</td>
                <td className="px-4 py-3 tabular-nums">{s.wealth_gap.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Equity tab**

Replace `website/src/components/explorer/tabs/Equity.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';

export default function Equity() {
  const [rows, setRows] = useState([]);
  useEffect(() => { loadData('scenarios').then(setRows); }, []);

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Equity</h2>
      <p className="text-muted max-w-3xl mb-8">
        Three metrics: Wagstaff concentration index, slope index of inequality (SII), and the poorest-richest wealth gap. Computed with survey weights (v005/1e6).
      </p>
      <div className="rounded-2xl border border-white/10 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-dusk">
            <tr className="text-left">
              <th className="px-4 py-3">Scenario</th>
              <th className="px-4 py-3 tabular-nums">Concentration</th>
              <th className="px-4 py-3 tabular-nums">SII</th>
              <th className="px-4 py-3 tabular-nums">Wealth gap</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t border-white/5">
                <td className="px-4 py-3">{r.id}</td>
                <td className="px-4 py-3 tabular-nums">{r.concentration_index.toFixed(3)}</td>
                <td className="px-4 py-3 tabular-nums">{r.slope_index.toFixed(3)}</td>
                <td className="px-4 py-3 tabular-nums">{r.wealth_gap.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Validation tab — disclose known limitation**

Replace `website/src/components/explorer/tabs/Validation.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';
import { formatPct } from '../../../lib/format.js';

export default function Validation() {
  const [data, setData] = useState(null);
  useEffect(() => { loadData('validation').then(setData); }, []);
  if (!data) return <div className="text-muted">Loading…</div>;

  const internal = data.internal || {};
  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Validation</h2>
      <div className={`rounded-2xl border p-6 mb-8 ${internal.passed ? 'border-verdigris/40 bg-verdigris/5' : 'border-terracotta/40 bg-terracotta/5'}`}>
        <div className="font-mono text-xs uppercase text-muted">Internal calibration</div>
        <div className="mt-2 font-serif text-3xl">
          Predicted {internal.predicted !== undefined ? formatPct(internal.predicted, 1) : '—'} · Observed {internal.observed !== undefined ? formatPct(internal.observed, 1) : '—'}
        </div>
        <div className="mt-2 text-sm">
          Absolute error: <span className="tabular-nums">{internal.absolute_error?.toFixed(4)}</span> (tolerance {internal.tolerance})
        </div>
        <div className="mt-1 text-sm font-semibold">{internal.passed ? 'PASS' : 'FAIL — known limitation'}</div>
        {!internal.passed && (
          <p className="mt-3 text-sm text-muted">
            The microsim over-predicts S0 DTP3 completion by ~5.6 percentage points. Absolute rates in the dashboard should be interpreted as relative comparisons rather than absolute predictions. See the manuscript's Discussion section.
          </p>
        )}
      </div>

      <h3 className="font-serif text-2xl mb-4">Subgroup calibration</h3>
      <div className="grid md:grid-cols-2 gap-4">
        {Object.entries(data.subgroups || {}).map(([name, rows]) => {
          const flagged = rows.filter((r) => r.flagged).length;
          return (
            <div key={name} className="rounded-2xl border border-white/10 bg-dusk/30 p-4">
              <div className="font-mono text-xs uppercase text-muted">{name}</div>
              <div className="mt-2 text-lg">{flagged} / {rows.length} strata flagged</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 7: Downloads tab**

Replace `website/src/components/explorer/tabs/Downloads.jsx`:

```jsx
const FILES = [
  { name: 'Scenarios (CSV)', href: '/dropout/data/scenarios.json', kind: 'JSON' },
  { name: 'Cascade (CSV)', href: '/dropout/data/cascade.json', kind: 'JSON' },
  { name: 'Scenario cube (JSON)', href: '/dropout/data/scenario_cube.json', kind: 'JSON' },
  { name: 'Validation report', href: '/dropout/data/validation.json', kind: 'JSON' },
  { name: 'Source code (GitHub)', href: 'https://github.com/olatechie/dropout', kind: 'Code' },
];

export default function Downloads() {
  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Downloads</h2>
      <p className="text-muted max-w-3xl mb-8">
        Raw data, scenario cube, and source code for replication.
      </p>
      <ul className="space-y-3">
        {FILES.map((f) => (
          <li key={f.href}>
            <a href={f.href} target={f.href.startsWith('http') ? '_blank' : '_self'} rel="noreferrer" className="flex items-center justify-between rounded-xl border border-white/10 bg-dusk/30 p-4 hover:border-saffron/40 transition">
              <span>{f.name}</span>
              <span className="text-xs font-mono text-muted">{f.kind}</span>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

- [ ] **Step 8: Commit**

```bash
git add website/src/components/explorer/tabs/
git commit -m "feat(web): explorer tabs — models, SHAP, RL, microsim, equity, validation, downloads"
```

---

### Task 12: Canvas foundation — StageCanvas, CinematicRig, lighting

**Files:**
- Create: `website/src/scene/StageCanvas.jsx`
- Create: `website/src/scene/camera/CinematicRig.jsx`
- Create: `website/src/scene/lighting/LightRig.jsx`
- Create: `website/src/scene/effects/Effects.jsx`

- [ ] **Step 1: StageCanvas**

Create `website/src/scene/StageCanvas.jsx`:

```jsx
import { Canvas } from '@react-three/fiber';
import { AdaptiveDpr, AdaptiveEvents, PerformanceMonitor } from '@react-three/drei';
import { Suspense, useState } from 'react';

export default function StageCanvas({ children, dpr = [1, 2], shadows = true, className = 'fixed inset-0 -z-0' }) {
  const [perfScore, setPerfScore] = useState(1);
  return (
    <div className={className}>
      <Canvas
        shadows={shadows}
        dpr={dpr}
        camera={{ position: [0, 1.5, 5], fov: 38 }}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
      >
        <PerformanceMonitor onChange={({ factor }) => setPerfScore(factor)} />
        <AdaptiveDpr pixelated />
        <AdaptiveEvents />
        <Suspense fallback={null}>
          {children}
        </Suspense>
      </Canvas>
    </div>
  );
}
```

- [ ] **Step 2: CinematicRig**

Create `website/src/scene/camera/CinematicRig.jsx`:

```jsx
import { useThree, useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import { Vector3 } from 'three';

// Per-act keyframes: position + target
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

  useFrame((_, dt) => {
    const key = ACT_KEYS[act] || ACT_KEYS[1];
    targetPos.current.set(...key.pos);
    targetLook.current.set(...key.look);
    camera.position.lerp(targetPos.current, Math.min(1, dt * 0.8));
    camera.lookAt(targetLook.current);
  });

  return null;
}
```

- [ ] **Step 3: LightRig**

Create `website/src/scene/lighting/LightRig.jsx`:

```jsx
const ACT_LIGHTING = {
  1: { keyColor: '#FFD3A0', intensity: 1.2, ambient: '#3A2A1A', ambientIntensity: 0.3 },
  2: { keyColor: '#F4F0E6', intensity: 1.0, ambient: '#1A2340', ambientIntensity: 0.4 },
  3: { keyColor: '#A5BFFF', intensity: 0.9, ambient: '#0D1220', ambientIntensity: 0.3 },
  4: { keyColor: '#FFD3A0', intensity: 1.1, ambient: '#1A2340', ambientIntensity: 0.4 },
  5: { keyColor: '#4A5568', intensity: 0.4, ambient: '#05070C', ambientIntensity: 0.2 },
};

export default function LightRig({ act = 1 }) {
  const lk = ACT_LIGHTING[act] || ACT_LIGHTING[1];
  return (
    <>
      <ambientLight intensity={lk.ambientIntensity} color={lk.ambient} />
      <directionalLight
        position={[5, 8, 4]}
        intensity={lk.intensity}
        color={lk.keyColor}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <hemisphereLight intensity={0.15} groundColor="#05070C" color={lk.keyColor} />
    </>
  );
}
```

- [ ] **Step 4: Effects composer**

Create `website/src/scene/effects/Effects.jsx`:

```jsx
import { EffectComposer, Bloom, DepthOfField, Vignette, Noise } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';

export default function Effects({ enabled = true }) {
  if (!enabled) return null;
  return (
    <EffectComposer>
      <Bloom intensity={0.6} luminanceThreshold={0.85} luminanceSmoothing={0.2} />
      <DepthOfField focusDistance={0.02} focalLength={0.05} bokehScale={2} />
      <Vignette eskil={false} offset={0.2} darkness={0.7} />
      <Noise opacity={0.05} blendFunction={BlendFunction.OVERLAY} />
    </EffectComposer>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add website/src/scene/
git commit -m "feat(web): 3D scene foundation — canvas, camera, lighting, postprocess"
```

---

### Task 13: Stylized figure props — Child, Mother, Home

Stylized low-poly figures using simple geometries (no external GLTF dependency yet — ship GLTFs as Task 14 polish).

**Files:**
- Create: `website/src/scene/props/Child.jsx`
- Create: `website/src/scene/props/Mother.jsx`
- Create: `website/src/scene/props/Home.jsx`
- Create: `website/src/scene/props/Clinic.jsx`

- [ ] **Step 1: Child (stylized low-poly)**

Create `website/src/scene/props/Child.jsx`:

```jsx
export default function Child({ position = [0, 0, 0], scale = 1, color = '#D4A574', glow = 0 }) {
  return (
    <group position={position} scale={scale}>
      <mesh castShadow position={[0, 0.55, 0]}>
        <sphereGeometry args={[0.15, 12, 12]} />
        <meshStandardMaterial color={color} emissive={glow > 0 ? '#F5B042' : '#000'} emissiveIntensity={glow} />
      </mesh>
      <mesh castShadow position={[0, 0.25, 0]}>
        <capsuleGeometry args={[0.12, 0.35, 4, 8]} />
        <meshStandardMaterial color="#C6553A" />
      </mesh>
    </group>
  );
}
```

- [ ] **Step 2: Mother**

Create `website/src/scene/props/Mother.jsx`:

```jsx
export default function Mother({ position = [0, 0, 0], scale = 1 }) {
  return (
    <group position={position} scale={scale}>
      <mesh castShadow position={[0, 1.65, 0]}>
        <sphereGeometry args={[0.18, 12, 12]} />
        <meshStandardMaterial color="#A66A2C" />
      </mesh>
      <mesh castShadow position={[0, 1.1, 0]}>
        <capsuleGeometry args={[0.22, 0.9, 4, 8]} />
        <meshStandardMaterial color="#F5B042" />
      </mesh>
      <mesh castShadow position={[0, 0.3, 0]}>
        <coneGeometry args={[0.35, 0.7, 6]} />
        <meshStandardMaterial color="#7A4A1E" />
      </mesh>
    </group>
  );
}
```

- [ ] **Step 3: Home**

Create `website/src/scene/props/Home.jsx`:

```jsx
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
```

- [ ] **Step 4: Clinic**

Create `website/src/scene/props/Clinic.jsx`:

```jsx
export default function Clinic({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      <mesh castShadow receiveShadow position={[0, 1, 0]}>
        <boxGeometry args={[3.5, 2, 2.5]} />
        <meshStandardMaterial color="#F4F0E6" roughness={0.7} />
      </mesh>
      <mesh position={[0, 2.1, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 0.6, 8]} />
        <meshStandardMaterial color="#47B7A0" />
      </mesh>
      <mesh position={[0, 2.5, 0]}>
        <boxGeometry args={[0.6, 0.1, 0.1]} />
        <meshStandardMaterial color="#47B7A0" />
      </mesh>
    </group>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add website/src/scene/props/
git commit -m "feat(web): stylized low-poly props — Child, Mother, Home, Clinic"
```

---

### Task 14: Act I scene — A Family

**Files:**
- Create: `website/src/scene/acts/ActI_Family.jsx`
- Modify: `website/src/routes/Story.jsx`

- [ ] **Step 1: Act I scene**

Create `website/src/scene/acts/ActI_Family.jsx`:

```jsx
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Environment, ContactShadows } from '@react-three/drei';
import Mother from '../props/Mother.jsx';
import Child from '../props/Child.jsx';
import Home from '../props/Home.jsx';

export default function ActI_Family({ progress = 0 }) {
  const glowRef = useRef(0);
  glowRef.current = progress > 0.5 ? (progress - 0.5) * 2 : 0;

  return (
    <>
      <Environment preset="sunset" />
      <fog attach="fog" args={['#0D1220', 5, 25]} />

      <Home position={[-3, 0, -2]} />

      <Mother position={[0, 0, 0]} />
      <Child position={[0.3, 0, 0.4]} scale={0.7} glow={glowRef.current} />

      <ContactShadows position={[0, 0.01, 0]} opacity={0.5} scale={10} blur={2} far={4} />

      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[40, 40]} />
        <meshStandardMaterial color="#1A2340" />
      </mesh>
    </>
  );
}
```

- [ ] **Step 2: Story route — wire Act I with scrollama**

Replace `website/src/routes/Story.jsx`:

```jsx
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
```

- [ ] **Step 3: Verify + commit**

Run: `cd website && npm run dev` → `/story`, verify home + mother + child render, scroll advances the scene.

```bash
git add website/src/routes/Story.jsx website/src/scene/acts/
git commit -m "feat(web): Story Act I — A Family — scene + scrollama wiring"
```

---

## Phase 3: Story Acts II–V · Design system polish (Week 3)

### Task 15: Cohort component (instanced mesh)

**Files:**
- Create: `website/src/scene/props/Cohort.jsx`

- [ ] **Step 1: Cohort with attrition**

Create `website/src/scene/props/Cohort.jsx`:

```jsx
import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Matrix4, Object3D } from 'three';

const tempObj = new Object3D();

export default function Cohort({ count = 1000, progress = 0, spread = 40 }) {
  const meshRef = useRef();

  const seeds = useMemo(() => {
    const s = [];
    for (let i = 0; i < count; i++) {
      s.push({
        x: (Math.random() - 0.5) * spread,
        z: (Math.random() - 0.5) * spread * 2,
        y: 0,
        dropStart: 0.2 + Math.random() * 0.6,
        dropRate: 0.05 + Math.random() * 0.1,
      });
    }
    return s;
  }, [count, spread]);

  useFrame(() => {
    if (!meshRef.current) return;
    for (let i = 0; i < seeds.length; i++) {
      const s = seeds[i];
      const dropping = progress > s.dropStart && (i / count) > progress;
      const yOffset = dropping ? -((progress - s.dropStart) * 10) : 0;
      tempObj.position.set(s.x, Math.max(s.y + yOffset, -5), s.z);
      tempObj.scale.setScalar(yOffset < -3 ? 0.01 : 0.3);
      tempObj.updateMatrix();
      meshRef.current.setMatrixAt(i, tempObj.matrix);
    }
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]} castShadow>
      <sphereGeometry args={[0.15, 8, 8]} />
      <meshStandardMaterial color="#F5B042" />
    </instancedMesh>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add website/src/scene/props/Cohort.jsx
git commit -m "feat(web): Cohort — instancedMesh with attrition animation"
```

---

### Task 16: Act II scene — The Corridor

**Files:**
- Create: `website/src/scene/acts/ActII_Corridor.jsx`
- Modify: `website/src/routes/Story.jsx`

- [ ] **Step 1: Act II scene**

Create `website/src/scene/acts/ActII_Corridor.jsx`:

```jsx
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import Cohort from '../props/Cohort.jsx';

export default function ActII_Corridor({ progress = 0 }) {
  const gateRef = useRef();
  useFrame((state) => {
    if (gateRef.current) gateRef.current.rotation.y += 0.005;
  });

  return (
    <>
      <fog attach="fog" args={['#0D1220', 10, 80]} />

      {/* Translucent floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
        <planeGeometry args={[60, 200]} />
        <meshStandardMaterial color="#1A2340" transparent opacity={0.5} />
      </mesh>

      {/* Gates at 6w, 10w, 14w */}
      {[-30, -10, 10, 30].map((z, i) => (
        <mesh key={z} position={[0, 3, z]} ref={i === 1 ? gateRef : null}>
          <torusGeometry args={[8, 0.2, 8, 32]} />
          <meshStandardMaterial color="#F5B042" emissive="#F5B042" emissiveIntensity={0.4} />
        </mesh>
      ))}

      <Cohort count={1000} progress={progress} spread={12} />
    </>
  );
}
```

- [ ] **Step 2: Wire Act II into Story**

Modify `website/src/routes/Story.jsx` — add import and second Scrollama step:

```jsx
import ActII_Corridor from '../scene/acts/ActII_Corridor.jsx';
```

In the JSX, after the Act I section:

```jsx
{currentAct === 2 && <ActII_Corridor progress={progress} />}
```

And a second `<Step data={2}>` in the Scrollama block:

```jsx
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
```

- [ ] **Step 3: Commit**

```bash
git add website/src/routes/Story.jsx website/src/scene/acts/ActII_Corridor.jsx
git commit -m "feat(web): Story Act II — The Corridor with cohort attrition"
```

---

### Task 17: Act III — Nation (TopoJSON extruded Nigeria)

**Files:**
- Create: `website/src/scene/acts/ActIII_Nation.jsx`
- Create: `website/src/scene/props/NigeriaMap.jsx`

- [ ] **Step 1: Nigeria extruded map**

Create `website/src/scene/props/NigeriaMap.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { useLoader } from '@react-three/fiber';
import { TextureLoader } from 'three';
import { feature } from 'topojson-client';
import { geoPath, geoMercator } from 'd3-geo';
import { loadData } from '../../lib/dataLoader.js';

export default function NigeriaMap() {
  const [geoJson, setGeoJson] = useState(null);
  const [cascade, setCascade] = useState(null);

  useEffect(() => {
    loadData('nigeria_zones').then((topo) => setGeoJson(feature(topo, topo.objects.states)));
    loadData('cascade').then(setCascade);
  }, []);

  if (!geoJson) return null;

  // Simple stand-in: colored extruded plane per state
  return (
    <group position={[0, 0, 0]} scale={0.08}>
      {geoJson.features.map((f, i) => (
        <mesh key={i} position={[0, 0, 0]}>
          <boxGeometry args={[2, 0.3 + (i % 10) * 0.1, 2]} />
          <meshStandardMaterial color="#C6553A" emissive="#C6553A" emissiveIntensity={0.2} />
        </mesh>
      ))}
    </group>
  );
}
```

(Note: this is a simplified stand-in. Full D3 geoPath extrusion to Three geometry is substantial; ship as stylized glow lattice for now and upgrade in Phase 5 polish.)

- [ ] **Step 2: Act III scene**

Create `website/src/scene/acts/ActIII_Nation.jsx`:

```jsx
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

export default function ActIII_Nation({ progress = 0 }) {
  const groupRef = useRef();
  useFrame(() => {
    if (groupRef.current) groupRef.current.rotation.y += 0.002;
  });

  return (
    <group ref={groupRef}>
      <fog attach="fog" args={['#05070C', 30, 200]} />

      {/* Lattice of light — many parallel corridors */}
      {Array.from({ length: 50 }).map((_, i) => (
        <mesh key={i} position={[(i - 25) * 3, 0, 0]}>
          <boxGeometry args={[0.1, 0.05, 60]} />
          <meshStandardMaterial
            color="#F5B042"
            emissive="#F5B042"
            emissiveIntensity={0.3 + Math.random() * 0.3}
            transparent
            opacity={0.7}
          />
        </mesh>
      ))}

      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[200, 200]} />
        <meshStandardMaterial color="#05070C" />
      </mesh>
    </group>
  );
}
```

- [ ] **Step 3: Wire Act III + commit**

Add `currentAct === 3 && <ActIII_Nation progress={progress} />` and a Step data={3} in `Story.jsx`.

```bash
git add website/src/scene/acts/ActIII_Nation.jsx website/src/scene/props/NigeriaMap.jsx website/src/routes/Story.jsx
git commit -m "feat(web): Story Act III — national lattice of light"
```

---

### Task 18: Act IV — Interventions with HUD

**Files:**
- Create: `website/src/scene/acts/ActIV_Interventions.jsx`
- Create: `website/src/components/hud/InterventionPanel.jsx`
- Create: `website/src/scene/props/InterventionEffect.jsx`

- [ ] **Step 1: InterventionEffect shader-ish effect**

Create `website/src/scene/props/InterventionEffect.jsx`:

```jsx
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

export default function InterventionEffect({ type, active, position = [0, 0, 0] }) {
  const ringRef = useRef();
  useFrame((state) => {
    if (!ringRef.current || !active) return;
    const t = state.clock.elapsedTime;
    ringRef.current.scale.setScalar(1 + Math.sin(t * 2) * 0.1);
  });

  if (!active) return null;

  const colors = {
    a1: '#F5B042', // SMS — saffron
    a2: '#47B7A0', // CHW — verdigris
    a3: '#5A7BFF', // Recall — iris
    a4: '#C6553A', // Incentive — terracotta
  };

  return (
    <mesh ref={ringRef} position={position}>
      <torusGeometry args={[2, 0.1, 8, 24]} />
      <meshStandardMaterial color={colors[type]} emissive={colors[type]} emissiveIntensity={0.8} transparent opacity={0.6} />
    </mesh>
  );
}
```

- [ ] **Step 2: InterventionPanel HUD**

Create `website/src/components/hud/InterventionPanel.jsx`:

```jsx
import { useScenarioStore } from '../../state/scenario.js';

const INTERVENTIONS = [
  { key: 'a1', label: 'SMS reminder', cost: 50, color: 'saffron' },
  { key: 'a2', label: 'CHW visit', cost: 500, color: 'verdigris' },
  { key: 'a3', label: 'Facility recall', cost: 1500, color: 'iris' },
  { key: 'a4', label: 'Incentive', cost: 800, color: 'terracotta' },
];

export default function InterventionPanel() {
  const interventions = useScenarioStore((s) => s.interventions);
  const toggle = useScenarioStore((s) => s.toggleIntervention);

  return (
    <div className="fixed left-6 top-1/2 -translate-y-1/2 z-20 rounded-2xl border border-white/10 bg-abyss/70 backdrop-blur-md p-4 w-64">
      <h3 className="font-serif text-lg mb-3">Interventions</h3>
      <ul className="space-y-2">
        {INTERVENTIONS.map((iv) => (
          <li key={iv.key}>
            <button
              onClick={() => toggle(iv.key)}
              className={`w-full text-left rounded-xl border p-3 transition ${
                interventions[iv.key]
                  ? `border-${iv.color} bg-${iv.color}/10`
                  : 'border-white/10 bg-dusk/30 hover:border-white/30'
              }`}
            >
              <div className="flex items-baseline justify-between">
                <span className="text-sm">{iv.label}</span>
                <span className="text-xs font-mono text-muted">₦{iv.cost}</span>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

- [ ] **Step 3: Act IV scene**

Create `website/src/scene/acts/ActIV_Interventions.jsx`:

```jsx
import { useScenarioStore } from '../../state/scenario.js';
import Cohort from '../props/Cohort.jsx';
import InterventionEffect from '../props/InterventionEffect.jsx';

export default function ActIV_Interventions({ progress = 0 }) {
  const interventions = useScenarioStore((s) => s.interventions);

  return (
    <>
      <fog attach="fog" args={['#1A2340', 8, 50]} />

      <Cohort count={100} progress={progress * 0.5} spread={8} />

      <InterventionEffect type="a1" active={interventions.a1} position={[0, 1, 5]} />
      <InterventionEffect type="a2" active={interventions.a2} position={[0, 1, 0]} />
      <InterventionEffect type="a3" active={interventions.a3} position={[0, 1, -5]} />
      <InterventionEffect type="a4" active={interventions.a4} position={[0, 1, -10]} />

      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[60, 60]} />
        <meshStandardMaterial color="#0D1220" />
      </mesh>
    </>
  );
}
```

- [ ] **Step 4: Wire into Story + commit**

Add to `Story.jsx`:

```jsx
import ActIV_Interventions from '../scene/acts/ActIV_Interventions.jsx';
import InterventionPanel from '../components/hud/InterventionPanel.jsx';

// In JSX:
{currentAct === 4 && (
  <>
    <ActIV_Interventions progress={progress} />
    <InterventionPanel />
  </>
)}
```

Add Step data={4} in Scrollama.

```bash
git add website/src/scene/acts/ActIV_Interventions.jsx website/src/scene/props/InterventionEffect.jsx website/src/components/hud/InterventionPanel.jsx website/src/routes/Story.jsx
git commit -m "feat(web): Story Act IV — interactive interventions + HUD"
```

---

### Task 19: Act V — Dashboard materializes

**Files:**
- Create: `website/src/scene/acts/ActV_Dashboard.jsx`
- Create: `website/src/components/hud/DashboardOverlay.jsx`

- [ ] **Step 1: DashboardOverlay — 6 cards that fade in**

Create `website/src/components/hud/DashboardOverlay.jsx`:

```jsx
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useScenarioStore } from '../../state/scenario.js';
import { formatNaira, formatPct } from '../../lib/format.js';
import { useEffect, useState } from 'react';
import { loadData } from '../../lib/dataLoader.js';
import { buildCubeIndex, interpolateScenario } from '../../lib/interp.js';

export default function DashboardOverlay({ visible = true }) {
  const [cube, setCube] = useState(null);
  const { budget, rule, sms_rrr, chw_rrr } = useScenarioStore();
  useEffect(() => { loadData('scenario_cube').then((r) => setCube(buildCubeIndex(r))); }, []);
  const live = cube ? interpolateScenario(cube, { budget, rule, sms_rrr, chw_rrr }) : null;

  const cards = [
    { label: 'Recommended', value: 'Risk-targeted CHW', sub: 'Top 30% risk → CHW, rest → SMS' },
    { label: 'DTP3 uplift', value: live ? formatPct(live.dtp3_mean, 1) : '—' },
    { label: 'ICER vs S0', value: '₦8,007', sub: 'per DTP3 completion' },
    { label: 'Budget', value: formatNaira(budget) },
    { label: 'Concentration index', value: live ? live.concentration_index.toFixed(3) : '—' },
    { label: 'Downloads', value: '→' },
  ];

  return (
    <motion.aside
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: visible ? 1 : 0, y: visible ? 0 : 40 }}
      transition={{ duration: 0.8, staggerChildren: 0.1 }}
      className="fixed bottom-8 inset-x-8 z-20 grid grid-cols-2 md:grid-cols-3 gap-4 max-w-6xl mx-auto"
    >
      {cards.map((c, i) => (
        <motion.div
          key={c.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08, duration: 0.4 }}
          className="rounded-2xl border border-white/10 bg-abyss/70 backdrop-blur-md p-4"
        >
          <div className="text-xs uppercase tracking-wider text-muted">{c.label}</div>
          <div className="mt-1 font-serif text-2xl tabular-nums">{c.value}</div>
          {c.sub && <div className="text-xs text-muted mt-1">{c.sub}</div>}
        </motion.div>
      ))}
      <div className="col-span-full flex gap-4 justify-center mt-4">
        <Link to="/policy" className="px-6 py-3 bg-saffron text-abyss rounded-full font-semibold hover:bg-saffron/90">See full dashboard →</Link>
        <Link to="/simulation" className="px-6 py-3 border border-white/20 rounded-full hover:bg-white/5">Try scenarios →</Link>
      </div>
    </motion.aside>
  );
}
```

- [ ] **Step 2: Act V scene (atmospheric background)**

Create `website/src/scene/acts/ActV_Dashboard.jsx`:

```jsx
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';

export default function ActV_Dashboard() {
  const meshRef = useRef();
  useFrame(() => {
    if (meshRef.current) meshRef.current.rotation.y += 0.0005;
  });

  return (
    <>
      <fog attach="fog" args={['#05070C', 20, 100]} />
      <group ref={meshRef}>
        {Array.from({ length: 200 }).map((_, i) => (
          <mesh key={i} position={[(Math.random() - 0.5) * 80, (Math.random()) * 20, (Math.random() - 0.5) * 80]}>
            <sphereGeometry args={[0.05, 4, 4]} />
            <meshBasicMaterial color="#F5B042" />
          </mesh>
        ))}
      </group>
    </>
  );
}
```

- [ ] **Step 3: Wire + commit**

Add to `Story.jsx`:

```jsx
import ActV_Dashboard from '../scene/acts/ActV_Dashboard.jsx';
import DashboardOverlay from '../components/hud/DashboardOverlay.jsx';

{currentAct === 5 && (
  <>
    <ActV_Dashboard />
    <DashboardOverlay visible />
  </>
)}
```

Add Step data={5}.

```bash
git add website/src/scene/acts/ActV_Dashboard.jsx website/src/components/hud/DashboardOverlay.jsx website/src/routes/Story.jsx
git commit -m "feat(web): Story Act V — dashboard materialises over atmospheric bg"
```

---

## Phase 4: Simulation · Transcript · Accessibility (Week 4)

### Task 20: Simulation sandbox

**Files:**
- Create: `website/src/routes/Simulation.jsx` (replace stub)
- Create: `website/src/components/hud/SimulationControls.jsx`
- Create: `website/src/scene/camera/OrbitRig.jsx`

- [ ] **Step 1: OrbitRig**

Create `website/src/scene/camera/OrbitRig.jsx`:

```jsx
import { OrbitControls } from '@react-three/drei';

export default function OrbitRig({ enabled = true }) {
  return <OrbitControls enabled={enabled} enablePan={true} enableZoom={true} maxDistance={100} minDistance={2} />;
}
```

- [ ] **Step 2: Controls panel**

Create `website/src/components/hud/SimulationControls.jsx`:

```jsx
import { useScenarioStore } from '../../state/scenario.js';
import BudgetSlider from './BudgetSlider.jsx';

export default function SimulationControls({ cameraMode, setCameraMode, scale, setScale }) {
  const { interventions, toggleIntervention, rule, setRule } = useScenarioStore();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-80 z-20 bg-abyss/80 backdrop-blur-lg border-r border-white/10 p-6 overflow-y-auto">
      <h2 className="font-serif text-2xl mb-6">Simulation</h2>

      <fieldset className="mb-6">
        <legend className="text-xs uppercase tracking-wider text-muted mb-2">Camera</legend>
        <div className="flex gap-2">
          {['orbit', 'flythrough', 'top'].map((m) => (
            <button key={m} onClick={() => setCameraMode(m)} className={`px-3 py-1 text-xs rounded-full border ${cameraMode === m ? 'border-saffron text-saffron' : 'border-white/10 text-muted'}`}>
              {m}
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset className="mb-6">
        <legend className="text-xs uppercase tracking-wider text-muted mb-2">Scale</legend>
        <select value={scale} onChange={(e) => setScale(e.target.value)} className="w-full bg-dusk border border-white/10 rounded-xl p-2">
          <option value="family">Family (1)</option>
          <option value="community">Community (100)</option>
          <option value="state">State (10k)</option>
          <option value="nation">Nation (3M particles)</option>
        </select>
      </fieldset>

      <fieldset className="mb-6">
        <legend className="text-xs uppercase tracking-wider text-muted mb-2">Interventions</legend>
        <div className="space-y-2">
          {['a1', 'a2', 'a3', 'a4'].map((k) => (
            <label key={k} className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={interventions[k]} onChange={() => toggleIntervention(k)} className="accent-saffron" />
              <span>{{ a1: 'SMS', a2: 'CHW', a3: 'Recall', a4: 'Incentive' }[k]}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset className="mb-6">
        <legend className="text-xs uppercase tracking-wider text-muted mb-2">Targeting rule</legend>
        <select value={rule} onChange={(e) => setRule(e.target.value)} className="w-full bg-dusk border border-white/10 rounded-xl p-2">
          <option value="uniform_sms">Uniform SMS</option>
          <option value="uniform_chw">Uniform CHW</option>
          <option value="top30_risk">Top-30% risk</option>
          <option value="top10_incentive">Top-10% + incentive</option>
          <option value="rl_optimised">RL-optimised</option>
        </select>
      </fieldset>

      <div className="mb-6"><BudgetSlider /></div>

      <button
        onClick={() => {
          const { encodeToURL } = useScenarioStore.getState();
          const url = `${window.location.origin}${window.location.pathname}?${encodeToURL()}`;
          navigator.clipboard.writeText(url);
        }}
        className="w-full py-2 border border-white/10 rounded-xl text-sm hover:border-saffron/40"
      >
        Copy snapshot URL
      </button>
    </aside>
  );
}
```

- [ ] **Step 3: Simulation route**

Replace `website/src/routes/Simulation.jsx`:

```jsx
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
```

- [ ] **Step 4: Commit**

```bash
git add website/src/routes/Simulation.jsx website/src/components/hud/SimulationControls.jsx website/src/scene/camera/OrbitRig.jsx
git commit -m "feat(web): simulation sandbox — orbit controls + snapshot URL"
```

---

### Task 21: Story transcript (accessible text-only alternative)

**Files:**
- Modify: `website/src/routes/Transcript.jsx`

- [ ] **Step 1: Build the transcript**

Replace `website/src/routes/Transcript.jsx`:

```jsx
export default function Transcript() {
  return (
    <main className="max-w-3xl mx-auto px-6 py-12 prose prose-invert">
      <h1 className="font-serif text-5xl">Story — Transcript</h1>
      <p className="text-muted">
        A text-only version of the cinematic story. All data conclusions in the policy dashboard remain identical.
      </p>

      <h2>Act I — A Family</h2>
      <p>
        In a home in Nigeria, a mother holds her newborn. Six weeks from birth, a decision begins:
        will this child complete the three-dose DTP vaccination series?
      </p>
      <p>Every year, 4.9 million children in Nigeria reach this moment.</p>

      <h2>Act II — The Corridor</h2>
      <p>
        The cascade runs from 6 to 14 weeks. At each dose, some children drop out.
        Nationally, 4.0% fail between DTP1 and DTP2. Another 3.9% fail between DTP2 and DTP3.
        Overall: 14.8% of children who receive DTP1 do not reach DTP3.
      </p>

      <h2>Act III — The Nation</h2>
      <p>
        Dropout varies sharply across Nigeria's six geopolitical zones.
        North Central: 19.6%. North East: 16.8%. South South: 8.6%.
        730,000 children drop out annually. Spatial clustering is weak — dropout is a diffuse phenomenon.
      </p>

      <h2>Act IV — The Interventions</h2>
      <p>
        Four evidence-based interventions can reduce dropout:
        SMS reminders (10% relative risk reduction),
        community health worker visits (20%),
        facility recall (25%),
        and conditional incentives (14%).
      </p>
      <p>
        Risk-targeted deployment — CHW for the top 30% predicted risk, SMS for the rest —
        is the most cost-effective strategy: 88.2% DTP3 completion at ₦8,007 per additional completion.
      </p>

      <h2>Act V — The Policy</h2>
      <p>
        The recommended policy: risk-targeted CHW allocation. All scenarios narrow the wealth-related
        inequality gap. The offline reinforcement learning policy (IQL) matches risk-targeted performance
        but at higher cost, reflecting the narrow action space available in the data.
      </p>

      <h2>Known limitation</h2>
      <p>
        Internal calibration: the microsim over-predicts S0 DTP3 completion by ~5.6 percentage points
        (predicted 91.0%, observed 85.4%). Absolute rates should be interpreted as relative comparisons.
      </p>
    </main>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add website/src/routes/Transcript.jsx
git commit -m "feat(web): story transcript — accessible text-only alternative"
```

---

### Task 22: Accessibility — reduced-motion + keyboard + skip-to

**Files:**
- Create: `website/src/hooks/useReducedMotion.js`
- Create: `website/src/components/shared/SkipLink.jsx`
- Modify: `website/src/scene/camera/CinematicRig.jsx`

- [ ] **Step 1: Reduced-motion hook**

Create `website/src/hooks/useReducedMotion.js`:

```js
import { useEffect, useState } from 'react';

export function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handle = () => setReduced(mq.matches);
    handle();
    mq.addEventListener('change', handle);
    return () => mq.removeEventListener('change', handle);
  }, []);
  return reduced;
}
```

- [ ] **Step 2: SkipLink**

Create `website/src/components/shared/SkipLink.jsx`:

```jsx
export default function SkipLink() {
  return (
    <a
      href="#main"
      className="sr-only focus:not-sr-only fixed top-2 left-2 z-50 px-4 py-2 bg-saffron text-abyss rounded"
    >
      Skip to main content
    </a>
  );
}
```

- [ ] **Step 3: Apply reduced-motion in CinematicRig**

Modify `website/src/scene/camera/CinematicRig.jsx`:

```jsx
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
```

- [ ] **Step 4: Wire SkipLink into Shell**

Modify `website/src/components/layout/Shell.jsx`:

```jsx
import Nav from './Nav.jsx';
import Footer from './Footer.jsx';
import SkipLink from '../shared/SkipLink.jsx';

export default function Shell({ children, showChrome = true }) {
  return (
    <div className="min-h-screen flex flex-col">
      <SkipLink />
      {showChrome && <Nav />}
      <main id="main" className={showChrome ? 'pt-16 flex-1' : 'flex-1'}>{children}</main>
      {showChrome && <Footer />}
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add website/src/hooks/ website/src/components/shared/SkipLink.jsx website/src/components/layout/Shell.jsx website/src/scene/camera/CinematicRig.jsx
git commit -m "feat(web): reduced-motion support + skip-to-main link"
```

---

### Task 23: WebGL detection + fallback redirect

**Files:**
- Create: `website/src/lib/webgl.js`
- Modify: `website/src/routes/Story.jsx`

- [ ] **Step 1: WebGL detection**

Create `website/src/lib/webgl.js`:

```js
export function hasWebGL() {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (canvas.getContext('webgl2') || canvas.getContext('webgl')));
  } catch {
    return false;
  }
}
```

- [ ] **Step 2: Fall back to transcript if no WebGL**

Modify `website/src/routes/Story.jsx`, at top:

```jsx
import { Navigate } from 'react-router-dom';
import { hasWebGL } from '../lib/webgl.js';

export default function Story() {
  if (!hasWebGL()) {
    return <Navigate to="/story/transcript" replace />;
  }
  // ... rest unchanged
}
```

- [ ] **Step 3: Commit**

```bash
git add website/src/lib/webgl.js website/src/routes/Story.jsx
git commit -m "feat(web): WebGL detection with automatic transcript fallback"
```

---

## Phase 5: Performance · CI · Analytics (Week 5)

### Task 24: Bundle analysis + manual chunk validation

**Files:**
- Modify: `website/vite.config.js` (verify chunks)
- Run: `npm run build && ls -la dist/assets/`

- [ ] **Step 1: Build and inspect**

Run:
```bash
cd website && npm run build
ls -la dist/assets/ | grep -E "\.js$" | sort -k5 -n
```

Expected: separate chunks for `three-core`, `three-react`, `charts`, `motion`, plus per-route chunks.

- [ ] **Step 2: Check sizes meet budget**

Core bundle (Policy/Explorer entry): <250KB gzipped. Lazy chunks (Story, Simulation): <900KB each.

If over budget, investigate imports — move heavy things to dynamic imports.

- [ ] **Step 3: Commit build artifacts are .gitignored, this step is verification only**

```bash
# no commit needed — budget validation only
```

---

### Task 25: Lighthouse CI

**Files:**
- Create: `website/.github/workflows/lighthouse.yml`
- Create: `website/lighthouserc.json`

- [ ] **Step 1: Lighthouse config**

Create `website/lighthouserc.json`:

```json
{
  "ci": {
    "collect": {
      "staticDistDir": "./dist",
      "url": [
        "http://localhost/dropout/",
        "http://localhost/dropout/policy",
        "http://localhost/dropout/explorer"
      ],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["warn", { "minScore": 0.85 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:best-practices": ["warn", { "minScore": 0.9 }]
      }
    }
  }
}
```

- [ ] **Step 2: GitHub Actions workflow**

Create `.github/workflows/website-lighthouse.yml` (at repo root, not website/):

```yaml
name: Website Lighthouse

on:
  pull_request:
    paths: ['website/**']
  push:
    branches: [main]
    paths: ['website/**']

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: cd website && npm ci
      - run: cd website && npm run build
      - run: npm install -g @lhci/cli
      - run: cd website && lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

- [ ] **Step 3: Commit**

```bash
git add website/lighthouserc.json .github/workflows/website-lighthouse.yml
git commit -m "ci: Lighthouse budget gate for website"
```

---

### Task 26: Plausible analytics

**Files:**
- Modify: `website/index.html`

- [ ] **Step 1: Add Plausible script (privacy-respecting)**

Edit `website/index.html` to add inside `<head>`:

```html
<script defer data-domain="olatechie.github.io" src="https://plausible.io/js/script.js"></script>
```

- [ ] **Step 2: Commit**

```bash
git add website/index.html
git commit -m "feat(web): add Plausible analytics (cookieless)"
```

---

## Phase 6: Polish · Deploy (Week 6)

### Task 27: GitHub Pages deploy

**Files:**
- Create: `website/scripts/deploy.sh`
- Create: `.github/workflows/website-deploy.yml`

- [ ] **Step 1: Deploy workflow**

Create `.github/workflows/website-deploy.yml`:

```yaml
name: Deploy Website

on:
  push:
    branches: [main]
    paths: ['website/**']

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: cd website && npm ci
      - run: cd website && npm run build
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./website/dist
          publish_branch: gh-pages
          destination_dir: dropout
```

- [ ] **Step 2: Local deploy helper**

Create `website/scripts/deploy.sh`:

```bash
#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
npm run build
npm run deploy
```

Run `chmod +x website/scripts/deploy.sh`.

- [ ] **Step 3: Commit**

```bash
git add website/scripts/deploy.sh .github/workflows/website-deploy.yml
git commit -m "ci: GitHub Pages deploy workflow"
```

---

### Task 28: Final verification

- [ ] **Step 1: Run full tests**

```bash
cd website && npm run test
```

Expected: all tests pass.

- [ ] **Step 2: Production build**

```bash
cd website && npm run build && npm run preview
```

Open http://localhost:4173/dropout/ and walk through all routes.

- [ ] **Step 3: Verify data files**

```bash
ls -la website/public/data/
```

Expected 9 JSON files: cascade, shap_summary, scenarios, icer, ceac, psa_summary, validation, cohort_sample, scenario_cube.

- [ ] **Step 4: Tag release**

```bash
git tag -a website-v0.1.0-rc -m "Cinematic dropout website — initial release candidate"
```

- [ ] **Step 5: Final commit**

If anything remains uncommitted, commit now:

```bash
git status
git add -A
git commit -m "chore: final polish before v0.1.0 deploy" || true
```
