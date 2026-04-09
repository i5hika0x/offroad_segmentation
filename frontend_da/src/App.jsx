import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Demo from './components/Demo';
import Architecture from './components/Architecture';

export default function App() {
  return (
    <div className="app-container">
      <Navbar />
      <Hero />
      <Demo />
      <Architecture />
    </div>
  );
}