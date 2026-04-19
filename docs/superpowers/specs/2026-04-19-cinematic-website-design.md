# Design Spec: Cinematic Dropout Website

**Date:** 2026-04-19
**Author:** Ola Uthman + Claude
**Status:** Approved (pending user review)

---

## 0. Context

**Project:** Nigeria DTP Vaccine Dropout RL Study — public-facing interactive website.

**Position within the trilogy:**
- `01_zero-dose` — website shipped (`sample_website/website` = "zerodose-nigeria"); reference for storytelling + dashboard polish.
- `02_mov` — website planned; this brief's blueprint will be reused.
- `03_dropout` — **this spec.** Scope: Dropout website only. MOV follows as a separate effort using the same framework.

**Pause note:** the manuscript update (Stage 2/3 v2 results integration into `manuscript/`) is deliberately paused. All effort directed at the website.

**Reference inputs:**
- `sample_website/website` — React + D3 + Framer Motion + scrollama; Story, Policy, Explorer architecture. Visual polish and scrollytelling reference.
- `sample_website/website_1` — React Three Fiber + drei + Zustand prototype with a `simulation/` folder. Cinematic 3D reference.
- Pipeline v2 outputs: `outputs/stage1/`, `outputs/stage2_v2/`, `outputs/stage3_v2/`, `outputs/validation/`.

## 1. Project Brief

### 1.1 Goal

Build a premium, cinematic, interactive digital experience that:
1. Communicates Nigeria's DTP1-to-DTP3 dropout problem to a public audience with emotional clarity.
2. Gives policymakers a tool to explore intervention strategies and their cost-effectiveness / equity trade-offs.
3. Gives researchers transparent access to methods, data, and reproducibility materials.

Not a basic informational site. A **cinematic digital product** that balances beauty with usability.

### 1.2 Audience (in priority order)

1. **Primary — Public, funders, media.** Emotional storytelling is the payload.
2. **Secondary — Policymakers, programme managers** (NPHCDA, Gavi, WHO AFRO).
3. **Tertiary — Researchers and peer reviewers.**

All three audiences served; cinematic framing is not diluted for the secondary/tertiary layers — they get their own dedicated routes.

### 1.3 Success criteria

- ≥5,000 unique visitors in first 90 days
- ≥30% of visitors reach Act V (story completion)
- ≥500 policy brief downloads in first 90 days
- External recognition: ≥15 shared snapshot URLs, ≥3 citations or policy references within 6 months
- Passes Lighthouse ≥85 (Story) / ≥95 (Policy, Explorer), WCAG AA

### 1.4 Non-goals

- Per-user accounts, auth, or saved sessions (URL-encoded state only).
- Real-time collaborative features.
- Native mobile apps (responsive web only; Tier 1 support for modern mobile browsers).
- Data entry or upload (read-only exploration of pre-computed outputs).

## 2. Experience Architecture

### 2.1 Four routes

| Route | Purpose | Primary audience | Build phase |
|-------|---------|------------------|-------------|
| `/` (Landing) | Brand entry, "Begin the story" CTA | All | 1 |
| `/story` | 5-act cinematic hero journey | Public, funders, media | 1 |
| `/policy` | Policymaker dashboard | NPHCDA, Gavi, WHO AFRO | 1 |
| `/simulation` | 3D sandbox for free exploration | Researchers, media, grant reviewers | 2 |
| `/explorer` | Tabbed researcher-grade data | Peer reviewers, academic readers | 2 |
| `/explorer/methods` | TRIPOD+AI methods | Academic readers | 2 |
| `/story/transcript` | Text-only accessible alternative | Non-WebGL users, screen readers | 1 |

### 2.2 Five-act story arc (`/story`)

| Act | Length | Scene | Key mechanic |
|-----|--------|-------|--------------|
| **I — A Family** | ~45s | Single Nigerian home at dusk; mother with newborn; DTP1 delivery | Intimate camera, warm lighting, single emotional anchor |
| **II — The Corridor** | ~60s | Cohort walks a temporal corridor through 6w/10w/14w gates; 15% fall away | Cohort attrition, per-child vignettes on click |
| **III — The Nation** | ~30s | Corridor zooms out to national lattice over 3D Nigeria map; zone dropout hotspots visible | Scale-reveal, 3D choropleth extrusion |
| **IV — The Interventions** | ~90s | Camera descends; user toggles SMS/CHW/recall/incentive; dashboard begins materializing | First interactive layer, scenario-cube interpolation, earned dashboard |
| **V — The Policy** | ~30s | Scene recedes to atmospheric background; full policy dashboard fades in | Narrative becomes tool; CTAs to Policy/Simulation/Explorer |

**Progressive disclosure:** the dashboard is not shown until the viewer has earned it through the story. Repeat visitors can "Skip to Dashboard" via a persistent floating pill.

### 2.3 Layered information density

| Layer | Where | Depth |
|-------|-------|-------|
| Cinematic / emotional | Landing + Story Acts I–III | One number, one metaphor, one feeling per beat |
| Applied / decision-oriented | Story Act IV–V + Policy | Scenario comparison, ICER, budget, equity |
| Methodological / reproducibility | Explorer + Methods | Full statistical content, downloads, citations |

Visitors self-select the depth they need.

## 3. Repository Structure

```
website/
├── package.json               # Vite + React 19 + R3F + drei + zustand + framer-motion + d3
├── vite.config.js             # Route-level code splitting for /simulation and /story
├── index.html
├── public/
│   ├── data/                  # Pre-computed JSON (see §4)
│   ├── models/                # glTF: mother, child, home, clinic, city_block
│   ├── textures/              # KTX2 stylized textures, HDRIs
│   └── fonts/                 # Fraunces, Inter, JetBrains Mono (variable)
├── src/
│   ├── App.jsx, main.jsx      # Router + global providers
│   ├── routes/                # Story, Policy, Simulation, Explorer, Methods, Landing
│   ├── scene/                 # R3F scene graph
│   │   ├── StageCanvas.jsx
│   │   ├── acts/              # ActI_Family, ActII_Corridor, ActIII_Nation, ActIV_Interventions, ActV_Dashboard
│   │   ├── props/             # Child, Mother, Clinic, Home, Intervention, Cohort
│   │   ├── camera/            # CinematicRig, OrbitRig
│   │   └── effects/           # Bloom, DOF, VolumetricLight, GroundFog
│   ├── components/
│   │   ├── hud/               # ActLabel, ScenarioToggle, BudgetSlider, MetricCard
│   │   ├── charts/            # CascadeBar, Choropleth, CEACCurve, ICERPlane, ShapBeeswarm, Tornado
│   │   ├── layout/            # Nav, Footer, SkipToPolicy
│   │   └── shared/            # Button, Pill, Tooltip
│   ├── state/                 # Zustand: story, scenario, interp
│   ├── lib/                   # interp, format, dataLoader, audio
│   └── styles/                # globals.css, theme.js
└── scripts/
    ├── prepare_website_data.py     # Pipeline outputs → tidy JSON
    ├── precompute_scenarios.py     # Scenario cube for what-if sliders
    └── optimize_assets.sh          # glTF draco, texture KTX2
```

## 4. Data Pipeline

### 4.1 `prepare_website_data.py` — pipeline exports → tidy JSON

| Pipeline source | Web output | Used in |
|-----------------|------------|---------|
| `outputs/stage1/cascade_metrics.csv` | `cascade.json` | Act II/III, Policy |
| `outputs/stage1/xgb_results_summary.json` | `shap_summary.json` | Explorer |
| `outputs/stage3_v2/microsim_results.csv` | `scenarios.json` | Policy, Act IV |
| `outputs/stage3_v2/icer_distribution.csv` | `icer.json` | Policy ICER plane |
| `outputs/stage3_v2/ceac_data.csv` | `ceac.json` | Policy |
| `outputs/stage3_v2/microsim_psa.csv` (thinned) | `psa_summary.json` | Policy CE-plane |
| `outputs/validation/*` | `validation.json` | Explorer |
| `outputs/stage1/trajectory_dataset.csv` (anonymised, n=100) | `cohort_sample.json` | Act II click vignettes |
| GADM NGA Level 1 shapefile (simplified) | `nigeria_zones.topojson` | Act III, Policy choropleth |

**Rules:** all floats rounded to 4dp; bootstrap arrays thinned to 250 entries; GeoJSON → TopoJSON (~70% smaller); gzip applied at deploy.

### 4.2 `precompute_scenarios.py` — scenario cube

Parameter grid:
- Budget: {₦250M, ₦500M, ₦750M, ₦1B, ₦1.5B} (5 levels)
- Targeting rule: {uniform SMS, uniform CHW, top-30% risk, top-10% + incentive, RL-optimised} (5 rules)
- SMS RRR: {low, central, high} from Beta prior (3 levels)
- CHW RRR: {low, central, high} (3 levels)

Total: 5 × 5 × 3 × 3 = **225 scenarios** × 100 bootstrap iterations.

**Output:** `scenario_cube.json` (~800KB gzipped).

### 4.3 Client-side interpolation (`src/lib/interp.js`)

Trilinear interpolation over (budget × sms_rrr × chw_rrr) within a chosen targeting rule. Returns interpolated DTP3 rate, cost/child, CI, concentration index in <1ms. Both cinematic scene and dashboard subscribe.

## 5. The Cinematic Hero — Act Details

### 5.1 Act I — A Family (~45s)
- **Scene:** Nigerian home at dusk, warm lamplight. Mother + newborn. Ground fog, soft bloom, HDRI rural sky.
- **Camera:** Slow dolly-in, settling at shoulder-height with DOF on mother's face.
- **Scroll cues:** 0% title card "Six weeks from birth, a decision begins." → 50% warm point of light enters child (DTP1) → 100% "Every year in Nigeria, 4.9 million children reach this moment."
- **Assets:** `mother.glb`, `baby.glb`, `home_interior.glb` (~1.2MB gzipped total).
- **Lighting:** Warm 2700K key, ambient fill, volumetric fog.
- **Post-processing:** Bloom (threshold 0.9), DOF, Vignette.

### 5.2 Act II — The Corridor (~60s)
- **Scene:** Translucent corridor of time with 6w, 10w, 14w, 12m gates. Cohort of mothers + children walks through. Starts at 100 visible, scales to 1,000 (InstancedMesh), then 10,000 (particle LOD).
- **Camera:** Tracking shot rising from shoulder-height to above-cohort view as count grows.
- **Attrition:** At 10w and 14w gates, 4% of cohort dims and drifts off-path (soft chime, capped for fatigue).
- **Interaction:** Click any child → vignette panel with one anonymised trajectory from `cohort_sample.json`.
- **Technical:** InstancedMesh with LOD swap at distance. Falling animation: per-instance opacity + gravity (~60 simultaneous GPU-friendly).

### 5.3 Act III — The Nation (~30s)
- **Scene:** Corridor becomes one of thousands, forming a lattice of light over dark 3D Nigeria map. Zone brightness encodes dropout rate. Slow orbit.
- **Camera:** Helicopter rise from 50m to 500m altitude.
- **Scroll cues:** "730,000 children drop out annually" → zone labels light up → "The villain is not neglect. It is a system that catches no one once they begin to fall."
- **Technical:** Extruded TopoJSON (37 state meshes, height = dropout rate). 1,000 GPU-instanced corridor segments with fragment-shader glow. Subtle cloud/atmosphere layer.

### 5.4 Act IV — The Interventions (~90s)
- **Scene:** Camera descends back into corridor on 100-child cohort. Floating intervention panel (glass-morph HUD) with four toggles: SMS, CHW, recall, incentive.
- **Per-intervention visual signature:**
  - SMS: soft pulse wave
  - CHW: walking figure joining each family briefly
  - Recall: beacon from clinic
  - Incentive: coin/voucher glow on family
- **Dashboard materialization:** DTP3 rate, cost/child, equity gap cards fade in at viewport bottom, live-bound to toggles.
- **Scroll arc:** Introduce each intervention sequentially → end with "Now what would you do with ₦500 million?"
- **Technical:** Per-intervention shader effect. Zustand `scenario.js` store → scene + HUD re-render. Scenario cube interpolation on state change.

### 5.5 Act V — The Policy (~30s)
- **Scene:** Camera pulls back to fixed high-angle. Scene becomes atmospheric background (low saturation, slow ambient motion).
- **UI:** Six dashboard cards fade in (Framer Motion staggered):
  1. Recommended policy headline
  2. DTP3 uplift vs S0 with 95% CI
  3. ICER with dominant-scenario badge
  4. Budget calculator + live cost
  5. Equity (concentration index, poorest-richest gap)
  6. Downloads (policy brief PDF, 1-page infographic, data bundle)
- **Scroll unlocks.** CTAs: "See full dashboard" → `/policy`; "Try different scenarios" → `/simulation`; "Read the methods" → `/explorer/methods`.

### 5.6 Act transitions
- No hard cuts. One continuous Bezier spline camera path across all acts.
- Lighting re-keys: Act I warm (2700K) → II neutral (5500K) → III cool dusk (4500K) → IV warm-neutral → V muted.
- Audio (opt-in): Act I crickets → II corridor breath/steps → III rising strings → IV heartbeat pulse → V ambient settle.
- `prefers-reduced-motion`: act transitions become 100ms fades; camera becomes cuts; attrition becomes static count updates.

## 6. Data-Forward Experiences

### 6.1 `/policy` — Policymaker dashboard

Dark cinematic background (Nigeria at night, desaturated + blurred, becomes chrome not content).

**Modules above fold (1440×900):**
- Hero recommendation banner
- Scenario comparison table (sortable by DTP3/cost/ICER/equity; hover animates background scene)
- Budget-to-outcome slider with ICER gauge
- Cost-effectiveness plane (PSA point cloud, dominance quadrant)
- Choropleth — Nigeria states coloured by DTP3 uplift under current config

**Below fold:**
- Equity pane (concentration index before/after, SII, quintile dumbbell)
- CEAC curves
- Download strip (PDF brief auto-generated with current slider config; scenario CSV; full data bundle; citation)

**Interaction:** slider debounced 150ms, interpolation 60fps; row hover subtly orbits background camera to match scenario.

### 6.2 `/simulation` — 3D sandbox

Full-screen canvas + left control panel + bottom metric strip.

**Controls (left panel, 320px glass-morph HUD):**
- Camera mode: Free orbit / Cinematic flythrough / Top-down map
- Scale: Family (1) / Community (100) / State (10K) / Nation (3M particles)
- Interventions: 4 toggle cards
- Targeting rule: dropdown (5 options)
- Budget slider
- Time-of-day lighting presets
- Effect sliders: bloom, DOF, fog, grain

**Metric strip (bottom):** live DTP3%, children saved, cost/child, concentration index, ICER vs S0.

**Features:**
- Click any child → probabilistic profile popup
- Share: "Snapshot URL" encodes current state (`/simulation?cam=orbit&scale=state&interventions=1,2&budget=500M`)
- Embed mode: `/simulation?embed=1` strips chrome for iframe use

### 6.3 `/explorer` — Researcher tabs

No 3D scene (or subtle corner thumbnail). Journal-supplement density.

**Tabs:** Cascade · Prediction Models · SHAP/Andersen · Offline RL · Microsim · Equity · Validation · Methods · Downloads.

Each chart interactive (hover, click, filter by zone); all have "copy data" + "download figure" buttons; every number shows bootstrap CI on hover.

**Validation tab explicitly discloses:** internal calibration failure (predicted 91.0% vs observed 85.4%); subgroup calibration results. No hiding known limitations.

## 7. Design System

### 7.1 Voice
- **Cinematic** (Acts I–III, landing): poetic, restrained, emotional.
- **Editorial** (Acts IV–V, Policy): plain, authoritative, concrete.
- **Scientific** (Explorer, Methods): precise, hedged, transparent.

No hype. RL framework honestly described as "sequential decision problem", not "breakthrough".

### 7.2 Colour palette

**Base (dark-first):**
- `bg.abyss` `#05070C` — deepest background
- `bg.night` `#0D1220` — dashboard background
- `bg.dusk` `#1A2340` — surface / card
- `fg.moonlight` `#F4F0E6` — primary text
- `fg.muted` `#9AA3B8` — secondary text

**Accents:**
- `acc.saffron` `#F5B042` — CTA, vaccine glow, DTP3 positive
- `acc.terracotta` `#C6553A` — dropout, risk hotspots
- `acc.iris` `#5A7BFF` — secondary action, cost/budget
- `acc.verdigris` `#47B7A0` — equity improvement, dominant badge
- `acc.ochre` `#A66A2C` — Nigerian earth tones in maps

**Data encoding (strict):** Warm→cool gradient for DTP3 completion; grey→terracotta for dropout; green→red for equity change (green narrow, red widen).

### 7.3 Typography
- **Fraunces** (serif, variable) — cinematic titles, display quotes
- **Inter** (sans, variable) — UI, body, data labels
- **JetBrains Mono** — tabular numbers, code

Fluid clamp-based type scale; `font-variant-numeric: tabular-nums` in all data contexts.

### 7.4 Motion
- `ease-cinema` `cubic-bezier(0.25, 0.46, 0.45, 0.94)` — camera, scene morphs
- `ease-ui` `cubic-bezier(0.4, 0, 0.2, 1)` — panels, cards
- `spring` Framer Motion (stiffness 180 / damping 22) — HUD entries, value counters

Durations: hover 150ms · panel 280ms · route 500ms · act 1.2s · camera dolly 2–4s.

### 7.5 Atmosphere & texture
- One key directional (warm, strong shadows) + fill + rim. Key colour-temp shifts per act.
- Soft contact shadows (drei `<ContactShadows>`).
- Low-poly stylized materials, flat-shaded with rim light.
- Fine dust particles drifting. Ember sparks at DTP3 moments.
- Post: Bloom (0.85/0.6), DOF, vignette, film grain (0.2), subtle chromatic aberration (0.002).
- HDRIs per act (warm dusk, neutral void, satellite Nigeria, soft day, blurred dashboard wallpaper).

### 7.6 Iconography
- Lucide icons for UI.
- Custom pictograms for interventions: SMS (phone wave), CHW (walking figure), recall (beacon), incentive (voucher). Flat saffron-on-dark.
- No stock photography; stills rendered from Three.js scene for brand unity.

### 7.7 Audio (opt-in)
- Ambient (per-act), interaction chimes, narration (phase 2; English default, potential Hausa/Yoruba/Igbo).
- Default off; first-visit HUD suggests enabling.

## 8. Performance

**Budgets (CI-enforced):**

| Metric | Target |
|--------|--------|
| FCP (Policy, Explorer) | <1.2s |
| LCP | <2.5s |
| FCP (Story) | <2.0s |
| Scene ready-to-interact (Story, 4G) | <5.0s |
| Frame rate | 60fps / 45fps floor |
| Initial JS bundle (Policy, Explorer) | <250KB gzipped |
| Lazy chunks (Story, Simulation) | <900KB each gzipped |
| Total transfer (Policy cold load) | <3MB |
| Total transfer (Story cold load) | <8MB |
| Lighthouse Performance | ≥85 Story / ≥95 Policy, Explorer |

**Optimization:**
- Vite manual chunks: `three-core`, `three-react`, `charts`, `motion`
- glTF → Draco; textures → KTX2 ETC1S (~70% and ~60% reductions)
- LOD via drei `<Detailed>` (hi/mid/particle for figures)
- InstancedMesh for 10k cohort (single draw call)
- `<AdaptiveDpr>` + `<AdaptiveEvents>` — reduce pixel ratio / throttle events on slow frames
- Post-processing disabled if FPS <45 for 2s
- Route prefetch on hover
- Data JSON gzipped; scenario_cube cached across routes

## 9. Accessibility

WCAG AA target; AAA where feasible.

- Keyboard navigation for all interactive elements; visible focus ring (saffron)
- Screen reader parallel text narration for every 3D scene (ARIA-live act titles)
- `prefers-reduced-motion`: disable camera dollies, attrition animations, bloom/DOF/grain
- Contrast ≥4.5:1 body, ≥3:1 large text & graphics (axe-core in CI)
- Never colour-only encoding (shape/position/pattern paired); viridis alt palette in Explorer
- Language markup per section (English default, Phase 2 translations)
- Skip links: "Skip to dashboard", "Skip to main content"

**Alternative experiences:**
- All data conclusions present in `/policy` + `/explorer` — cinematic is additive
- `/story/transcript` renders Acts I–V as text + static charts (fully accessible)

## 10. Browser & device support

| Tier | Scope |
|------|-------|
| Tier 1 | Latest Chrome/Safari/Edge, desktop + iPad + iPhone 13+; full experience |
| Tier 2 | Latest Firefox, Android mid-range, older iOS/iPad; reduced post-processing |
| Tier 3 | No WebGL; auto-redirect to `/story/transcript` + `/policy` with static SVG alternatives |

Detection on boot via WebGL context probe.

## 11. Deployment

- **GitHub Pages** static hosting at `olatechie.github.io/dropout/`. No custom domain.
- Vite `base: '/dropout/'` configured; all asset and router paths use this base.
- **CI (GitHub Actions):** test → Lighthouse CI (budgets enforced) → axe-core → build → deploy to `gh-pages`.
- **Pre-deploy gates:** all budgets met; all a11y tests pass; data JSON schema-valid; 3D assets under 2MB each.

## 12. Privacy & analytics

- **Plausible Analytics** — no cookies, GDPR-compliant, <1KB.
- Tracks: route transitions, act completion, scenario toggles/budget values, downloads. No PII. No third-party cookies. Warwick policy-compliant.

## 13. Phased delivery

Full build in 4–6 weeks, **all four experiences production-grade**. Internal milestones for review:

| Week | Milestone |
|------|-----------|
| 1 | Scaffold + data pipeline + landing + Policy MVP (charts + slider without 3D background) |
| 2 | Explorer tabs (no 3D); Story Act I + II fully built |
| 3 | Story Acts III, IV, V complete; design system finalised |
| 4 | Simulation sandbox; /story/transcript fallback; accessibility audit |
| 5 | Performance optimization; Lighthouse budget enforcement; cross-device QA |
| 6 | Ethics/policy review, external feedback, content polish, deploy |

## 14. Risk register

| Risk | Mitigation |
|------|------------|
| 3D scene too heavy on mid-range Android | Auto-LOD, fallback route, tier detection |
| Emotional content reads as manipulative | External review by Nigerian team; Act I script vetted |
| Scenario cube too large | Reduce grid density; lazy-load slices |
| Cinematic feels slick without substance | Explorer rich; every cinematic claim linked to methods |
| GitHub Pages routing breaks | HashRouter fallback, CI tested |
| Internal calibration gap (5.6pp) undermines trust | Disclosed prominently in Explorer → Validation; acknowledged in Policy footer |

## 15. Success metrics (90-day post-launch)

- ≥5,000 unique visitors
- ≥30% reach Act V
- ≥500 policy brief downloads
- ≥15 shared `/simulation?snapshot=...` URLs publicly (embeds in media/grants)
- ≥3 citations or policy references within 6 months

## 16. Out of scope

- Manuscript update (paused).
- MOV website (follows separately with this blueprint).
- Backend services (scenario cube is pre-computed).
- User accounts, saved sessions beyond URL state.
- Native mobile apps.
- Data entry / upload / editing.
- Full Phase 2 translations (English-only at launch; framework ready for Phase 2).
