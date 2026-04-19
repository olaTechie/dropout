import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center text-center px-6">
      <h1 className="font-serif text-6xl md:text-8xl leading-tight max-w-4xl">
        Catching the Fall
      </h1>
      <p className="mt-6 text-xl text-muted max-w-2xl">
        Why children drop out of vaccination in Nigeria — and what to do about it.
      </p>
      <Link
        to="/story"
        className="mt-12 inline-flex items-center gap-2 px-8 py-4 bg-saffron text-abyss font-semibold rounded-full hover:bg-saffron/90 transition"
      >
        Begin the story →
      </Link>
    </main>
  );
}
