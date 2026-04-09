import './Architecture.css';

const STAGES = [
    {
        id: '01',
        title: 'Input Stage',
        desc: 'Uploads terrain image/ off-road scene'
    },
    {
        id: '02',
        title: 'AI Feature Extraction',
        desc: 'DINOV2 extracts deep visual features from terrain'
    },
    {
        id: '03',
        title: 'Scene Understanding',
        desc: '(Segmentation) Classifies terrain into road, rocks, mud, obstacles'
    },
    {
        id: '04',
        title: 'Output',
        desc: 'Safe paths, overlays, and terrain insights with confidence scores'
    }
];

export default function Architecture() {
    return (
        <section id="architecture" className="arch-section">
            <div className="arch-header">
                <h2 className="section-title">Architecture</h2>
                <p className="stat-label" style={{ marginBottom: '0.5rem' }}>PROCESSING PIPELINE</p>
                <p style={{ color: 'var(--text-muted)' }}>From Pixels to Paths - Watch AI Understand Your Terrain</p>
            </div>

            <div className="arch-grid">
                {STAGES.map((stage) => (
                    <div key={stage.id} className="arch-card">
                        <div className="arch-num">{stage.id}</div>
                        <h3>{stage.title}</h3>
                        <p>{stage.desc}</p>
                    </div>
                ))}
            </div>
        </section>
    );
}