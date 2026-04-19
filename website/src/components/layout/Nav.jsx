import { useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';

const navItems = [
  { to: '/story', label: 'Story' },
  { to: '/policy', label: 'Policy' },
  { to: '/simulation', label: 'Simulation' },
  { to: '/explorer', label: 'Explorer' },
];

export default function Nav() {
  const [open, setOpen] = useState(false);
  const location = useLocation();

  // Close mobile menu on navigation
  const close = () => setOpen(false);

  return (
    <nav className="fixed top-0 inset-x-0 z-50 bg-abyss/70 backdrop-blur-md border-b border-white/5">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        <Link to="/" className="font-serif text-xl" onClick={close}>Catching the Fall</Link>

        {/* Desktop nav */}
        <ul className="hidden sm:flex items-center gap-6 text-sm">
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

        {/* Mobile toggle */}
        <button
          type="button"
          aria-expanded={open}
          aria-controls="mobile-nav"
          aria-label={open ? 'Close menu' : 'Open menu'}
          onClick={() => setOpen((o) => !o)}
          className="sm:hidden p-2 -mr-2 text-muted hover:text-moonlight focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-saffron/60 rounded"
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

      {/* Mobile drawer */}
      {open && (
        <ul
          id="mobile-nav"
          className="sm:hidden border-t border-white/5 bg-abyss/95 backdrop-blur-md px-6 py-4 space-y-3 text-base"
        >
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                onClick={close}
                className={({ isActive }) =>
                  `block py-1 ${isActive ? 'text-saffron' : 'text-muted hover:text-moonlight'}`
                }
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
}
