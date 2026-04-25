import "./Header.css";

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-logo">
          <span className="header-icon">🎵</span>
          <span className="header-title">Music Viber</span>
          <span className="header-badge">AI</span>
        </div>
        <p className="header-sub">Describe what you want to hear. Let AI do the rest.</p>
      </div>
    </header>
  );
}
