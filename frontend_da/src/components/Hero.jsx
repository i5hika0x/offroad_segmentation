import './Hero.css';

export default function Hero() {
    return (
        <section className="hero">
            <h1>
                <span className="text-silver">Mapping Reality</span> <br />
                <span className="text-gradient">Pixel By Pixel</span>
            </h1>
            <p className="hero-subtitle">
                Advanced semantic segmentation that interprets visual scenes with unprecedented accuracy.
                Powering the next generation of autonomous systems.
            </p>

            <a href="#demo" className="btn-primary tech-font">
                EXPLORE DEMO
            </a>

            <div className="stats-container">
                <div className="stat-item">
                    <div className="stat-value">10+</div>
                    <div className="stat-label">CLASSES</div>
                </div>
                <div className="stat-item">
                    <div className="stat-value">10 ms</div>
                    <div className="stat-label">INFERENCE TIME</div>
                </div>
                <div className="stat-item">
                    <div className="stat-value">%</div>
                    <div className="stat-label">MIOU SCORE</div>
                </div>
            </div>
        </section>
    );
}