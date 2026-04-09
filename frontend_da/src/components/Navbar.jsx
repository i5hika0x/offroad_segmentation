import './Navbar.css';

export default function Navbar() {
    return (
        <header className="navbar-container">
            <nav className="navbar">
                <a href="/" className="navbar-brand">
                    Seg<span>Vision</span>
                </a>

                <div className="navbar-nav">
                    <a href="#architecture" className="nav-link">Architecture</a>
                    <a href="#demo" className="nav-link">Demo</a>
                </div>
            </nav>
        </header>
    );
}