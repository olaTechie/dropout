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
