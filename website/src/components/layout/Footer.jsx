import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="relative border-t border-white/8 bg-black/10 px-6 py-10 text-sm text-muted">
      <div className="max-w-7xl mx-auto grid gap-8 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
        <div>
          <div className="text-[0.7rem] uppercase tracking-[0.24em] text-saffron">Open evidence platform</div>
          <div className="mt-3 font-serif text-2xl text-moonlight">Vaccination dropout, intervention logic, and policy tradeoffs in one place.</div>
          <p className="mt-3 max-w-2xl">
            University of Warwick · Warwick Applied Health · 2026
          </p>
        </div>

        <div className="flex flex-wrap gap-3 md:justify-end">
          <Link to="/explorer/methods" className="rounded-full border border-white/10 px-4 py-2 hover:border-saffron/40 hover:text-moonlight">
            Methods
          </Link>
          <a
            href="https://github.com/olatechie/dropout"
            className="rounded-full border border-white/10 px-4 py-2 hover:border-saffron/40 hover:text-moonlight"
            target="_blank"
            rel="noreferrer"
          >
            Code
          </a>
          <Link to="/story/transcript" className="rounded-full border border-white/10 px-4 py-2 hover:border-saffron/40 hover:text-moonlight">
            Transcript
          </Link>
        </div>
      </div>
    </footer>
  );
}
