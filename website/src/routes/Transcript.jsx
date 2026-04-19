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
