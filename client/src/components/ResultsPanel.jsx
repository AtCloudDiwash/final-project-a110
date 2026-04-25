import "./ResultsPanel.css";

const GENRE_COLORS = {
  pop: "#ec4899", lofi: "#14b8a6", rock: "#ef4444", ambient: "#6366f1",
  jazz: "#f59e0b", synthwave: "#a855f7", "indie pop": "#22c55e",
  "hip-hop": "#eab308", "r&b": "#f472b6", classical: "#d4a055",
  edm: "#06b6d4", country: "#84cc16", folk: "#6ee7b7",
  reggae: "#4ade80", metal: "#f87171",
};

function GenreBadge({ genre }) {
  const color = GENRE_COLORS[genre] || "#94a3b8";
  return (
    <span className="badge" style={{ color, borderColor: `${color}40`, background: `${color}12` }}>
      {genre}
    </span>
  );
}

function MoodBadge({ mood }) {
  return <span className="badge mood-badge">{mood}</span>;
}

function ScoreBar({ score }) {
  const max = 12;
  const pct = Math.min((score / max) * 100, 100);
  return (
    <div className="score-bar-wrap">
      <div className="score-bar">
        <div className="score-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="score-num">{score.toFixed(1)}</span>
    </div>
  );
}

function SongCard({ result, rank }) {
  const { song, score, explanation, reasons } = result;
  const text = explanation && explanation !== reasons ? explanation : null;

  return (
    <div className="song-card">
      <div className="song-rank">#{rank}</div>
      <div className="song-body">
        <div className="song-meta">
          <div className="song-title-row">
            <span className="song-title">{song.title}</span>
            <GenreBadge genre={song.genre} />
            <MoodBadge mood={song.mood} />
          </div>
          <span className="song-artist">{song.artist} · {song.release_decade}s</span>
        </div>
        <ScoreBar score={score} />
        {text && (
          <p className="song-explanation">
            <span className="ai-icon">✦</span> {text}
          </p>
        )}
      </div>
    </div>
  );
}

export default function ResultsPanel({ results, warnings, prefs, diff, onFeedback }) {
  return (
    <div className="results-panel">
      <div className="results-header">
        <h2 className="results-title">Recommendations</h2>
        {prefs && (
          <div className="prefs-summary">
            <span className="pref-chip">{prefs.genre}</span>
            <span className="pref-chip">{prefs.mood}</span>
            <span className="pref-chip">energy {prefs.energy?.toFixed?.(2)}</span>
            {prefs.likes_acoustic && <span className="pref-chip">acoustic</span>}
          </div>
        )}
      </div>

      {diff && Object.keys(diff).length > 0 && (
        <div className="diff-banner">
          <span className="diff-icon">🔄</span>
          <span>Adjusted: </span>
          {Object.entries(diff).map(([k, [a, b]]) => (
            <span key={k} className="diff-item">
              {k}: <s>{String(a)}</s> → <strong>{String(b)}</strong>
            </span>
          ))}
        </div>
      )}

      {warnings?.length > 0 && (
        <div className="warnings-banner">
          <span className="warn-icon">⚠</span>
          <div className="warn-list">
            {warnings.map((w, i) => <p key={i}>{w}</p>)}
          </div>
        </div>
      )}

      <div className="song-list">
        {results.map((r, i) => (
          <SongCard key={r.song.id ?? i} result={r} rank={i + 1} />
        ))}
      </div>

      <div className="satisfied-row">
        <span className="satisfied-label">Were these helpful?</span>
        <button className="btn-satisfied yes" onClick={() => onFeedback("yes")}>
          👍 Yes
        </button>
        <button className="btn-satisfied no" onClick={() => onFeedback("no")}>
          👎 No
        </button>
      </div>
    </div>
  );
}
