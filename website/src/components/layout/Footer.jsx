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
