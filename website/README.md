# Dropout Website

Cinematic interactive website for the Nigeria DTP1 to DTP3 vaccine dropout study (Warwick Applied Health, Warwick Medical School). Built with Vite, React 19, React Three Fiber, Zustand, Tailwind, and Recharts.

Production URL: https://olatechie.github.io/dropout/

## Run locally

```bash
cd website
npm install --legacy-peer-deps
npm run dev
```

Dev server: http://localhost:5173/dropout/

`--legacy-peer-deps` is required because `@react-three/drei` still declares React 18 as a peer while the app runs on React 19.

## Build

```bash
cd website
npm run build        # emits website/dist (~2 MB)
npm run preview      # serves dist at http://localhost:4173/dropout/
```

## Test

```bash
cd website
npx vitest run       # unit tests (interp, dataLoader, scenario store, format)
```

## Deploy

- **Automatic (preferred):** push to `main` with changes under `website/**`. The GitHub Actions workflow `.github/workflows/website-deploy.yml` builds and publishes to the `gh-pages` branch under `/dropout/`.
- **Manual:** `./website/scripts/deploy.sh` — runs `npm run build` then `npm run deploy` (`gh-pages -d dist`).

## Data preparation

Data JSONs live in `website/public/data/` and are built by two Python scripts:

```bash
# Fast (<1 min): materialises the 8 core JSON artefacts consumed by Policy/Explorer/Story
python website/scripts/prepare_website_data.py

# Long-running (hours): generates scenario_cube.json (225 configs) for the what-if sliders
python website/scripts/precompute_scenarios.py
```

Core artefacts currently materialised:

- `cascade.json` · `shap_summary.json` · `scenarios.json` · `icer.json`
- `ceac.json` · `psa_summary.json` · `validation.json` · `cohort_sample.json`

`scenario_cube.json` is optional at runtime. When absent, the Simulation route falls back to the discrete `scenarios.json` values without client-side trilinear interpolation.

## Routes

| Path | Description |
|------|-------------|
| `/` | Landing page |
| `/story` | 5-act Three.js hero journey (scrollama-driven, lazy loaded) |
| `/story/transcript` | Accessible text transcript of the Story route |
| `/policy` | Fast policy brief MVP with headline metrics and cascade |
| `/simulation` | Interactive what-if sandbox (lazy loaded, uses scenario cube when present) |
| `/explorer` | 8-tab data explorer (cascade, SHAP, scenarios, ICER, CEAC, PSA, validation, cohort) |
| `/explorer/methods` | Methods, assumptions, and reproducibility notes |

## Known limitations

- **Calibration gap (5.6 pp):** the underlying XGBoost dropout classifier shows a ~5.6 percentage-point gap between predicted and observed dropout in the lowest-risk decile after isotonic recalibration. Users should treat individual risk scores as ordinal rather than absolute probabilities. See `/explorer/methods` and the calibration figures in `outputs/stage1/` for full disclosure.
- The scenario cube is precomputed offline and interpolated trilinearly in the browser; sliders outside the convex hull of the 225 training configurations extrapolate and are flagged in the UI.
- WebGL is required for `/story` and `/simulation`; both routes fall back to a static illustration with a link to the transcript when WebGL is unavailable.

## Accessibility

Targets WCAG 2.1 AA. All interactive controls are keyboard reachable, `prefers-reduced-motion` disables camera flights and parallax, and every Three.js scene has a text transcript equivalent under `/story/transcript`.
