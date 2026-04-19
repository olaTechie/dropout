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
