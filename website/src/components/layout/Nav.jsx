import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';

const navItems = [
  { to: '/story', label: 'Story' },
  { to: '/policy', label: 'Policy' },
  { to: '/simulation', label: 'Simulation' },
  { to: '/explorer', label: 'Explorer' },
];

export default function Nav() {
  const [open, setOpen] = useState(false);

  const close = () => setOpen(false);

  return (
    <nav className="fixed top-0 inset-x-0 z-50 border-b border-white/8 bg-abyss/55 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between gap-4 rounded-full border border-white/10 bg-white/5 px-4 py-3 shadow-[0_12px_50px_rgba(0,0,0,0.24)]">
          <Link to="/" className="min-w-0" onClick={close}>
            <div className="text-[0.65rem] uppercase tracking-[0.26em] text-saffron">Catching the Fall</div>
            <div className="truncate font-serif text-lg leading-tight">Nigeria Vaccine Dropout Atlas</div>
          </Link>

          <ul className="hidden md:flex items-center gap-2 text-sm">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    `inline-flex rounded-full px-4 py-2 transition ${
                      isActive
                        ? 'bg-saffron text-abyss font-semibold shadow-[0_8px_30px_rgba(245,176,66,0.28)]'
                        : 'text-muted hover:bg-white/6 hover:text-moonlight'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>

          <div className="hidden lg:flex items-center gap-3 text-xs uppercase tracking-[0.18em] text-muted">
            <span className="rounded-full border border-verdigris/30 bg-verdigris/10 px-3 py-1 text-verdigris">Research site</span>
            <span>Interactive evidence</span>
          </div>

          <button
            type="button"
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? 'Close menu' : 'Open menu'}
            onClick={() => setOpen((o) => !o)}
            className="md:hidden rounded-full border border-white/10 bg-white/5 p-2 text-muted hover:text-moonlight focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-saffron/60"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              {open ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </>
              ) : (
                <>
                  <line x1="3" y1="6" x2="21" y2="6" />
                  <line x1="3" y1="12" x2="21" y2="12" />
                  <line x1="3" y1="18" x2="21" y2="18" />
                </>
              )}
            </svg>
          </button>
        </div>

        {open && (
          <div
            id="mobile-nav"
            className="mt-3 rounded-3xl border border-white/10 bg-night/95 p-4 shadow-2xl md:hidden"
          >
            <ul className="space-y-2 text-base">
              {navItems.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    onClick={close}
                    className={({ isActive }) =>
                      `block rounded-2xl px-4 py-3 ${
                        isActive
                          ? 'bg-saffron text-abyss font-semibold'
                          : 'bg-white/4 text-muted hover:bg-white/7 hover:text-moonlight'
                      }`
                    }
                  >
                    {item.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </nav>
  );
}
