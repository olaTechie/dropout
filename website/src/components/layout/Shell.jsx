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
