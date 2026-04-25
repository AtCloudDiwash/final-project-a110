import { useState } from "react";
import "./InputPanel.css";

const GENRES    = ["pop","lofi","rock","ambient","jazz","synthwave","indie pop","hip-hop","r&b","classical","edm","country","folk","reggae","metal"];
const MOODS     = ["happy","chill","intense","relaxed","focused","moody","calm"];
const MOOD_TAGS = ["euphoric","focused","peaceful","aggressive","energetic","dreamy","nostalgic","melancholic","uplifting"];
const DECADES   = [1990, 2000, 2010, 2020];
const MODES     = ["balanced","genre_first","mood_first","energy_focused"];

const DEFAULT_PROFILE = {
  genre: "lofi", mood: "chill", energy: 0.4,
  likes_acoustic: true, preferred_decade: null, preferred_mood_tag: null,
};

function Toggle({ checked, onChange }) {
  return (
    <label className="toggle-label" onClick={e => e.stopPropagation()}>
      <input type="checkbox" checked={checked} onChange={onChange} />
      <span className="toggle-track"><span className="toggle-thumb" /></span>
    </label>
  );
}

export default function InputPanel({ onSubmit, loading }) {
  const [profile, setProfile]           = useState(DEFAULT_PROFILE);
  const [useQuery, setUseQuery]         = useState(false);
  const [useSongs, setUseSongs]         = useState(false);
  const [query, setQuery]               = useState("");
  const [songInput, setSongInput]       = useState("");
  const [songTags, setSongTags]         = useState([]);
  const [mode, setMode]                 = useState("balanced");

  function randomize() {
    setProfile({
      genre: GENRES[Math.floor(Math.random() * GENRES.length)],
      mood:  MOODS[Math.floor(Math.random() * MOODS.length)],
      energy: Math.round((Math.random() * 0.9 + 0.1) * 100) / 100,
      likes_acoustic: Math.random() > 0.5,
      preferred_decade: Math.random() > 0.5 ? DECADES[Math.floor(Math.random() * DECADES.length)] : null,
      preferred_mood_tag: Math.random() > 0.5 ? MOOD_TAGS[Math.floor(Math.random() * MOOD_TAGS.length)] : null,
    });
  }

  function addTag(e) {
    if ((e.key === "Enter" || e.key === ",") && songInput.trim()) {
      e.preventDefault();
      const val = songInput.replace(/,$/, "").trim();
      if (val && !songTags.includes(val)) setSongTags([...songTags, val]);
      setSongInput("");
    }
  }

  function removeTag(t) { setSongTags(songTags.filter(x => x !== t)); }

  function handleSubmit() {
    const q     = useQuery && query.trim()   ? query.trim()   : null;
    const songs = useSongs && songTags.length ? songTags : null;
    onSubmit({ profile, query: q, songs, mode });
  }

  return (
    <div className="input-panel">

      {/* ── Profile ── */}
      <div className="section-header">
        <span className="section-title">Your Profile</span>
        <button className="btn-random" onClick={randomize}>🎲 Randomize</button>
      </div>

      <div className="profile-body">
        <div className="row-2">
          <div className="field">
            <label className="field-label">Genre</label>
            <select className="select-input" value={profile.genre}
              onChange={e => setProfile({ ...profile, genre: e.target.value })}>
              {GENRES.map(g => <option key={g}>{g}</option>)}
            </select>
          </div>
          <div className="field">
            <label className="field-label">Mood</label>
            <select className="select-input" value={profile.mood}
              onChange={e => setProfile({ ...profile, mood: e.target.value })}>
              {MOODS.map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
        </div>

        <div className="field">
          <label className="field-label">
            Energy
            <span className="slider-val">{profile.energy.toFixed(2)}</span>
          </label>
          <input type="range" min="0" max="1" step="0.01" className="slider"
            value={profile.energy}
            onChange={e => setProfile({ ...profile, energy: parseFloat(e.target.value) })} />
          <div className="slider-labels"><span>Calm</span><span>Intense</span></div>
        </div>

        <div className="row-3">
          <div className="field">
            <label className="field-label">Decade</label>
            <select className="select-input" value={profile.preferred_decade ?? ""}
              onChange={e => setProfile({ ...profile, preferred_decade: e.target.value ? parseInt(e.target.value) : null })}>
              <option value="">Any</option>
              {DECADES.map(d => <option key={d} value={d}>{d}s</option>)}
            </select>
          </div>
          <div className="field">
            <label className="field-label">Mood Tag</label>
            <select className="select-input" value={profile.preferred_mood_tag ?? ""}
              onChange={e => setProfile({ ...profile, preferred_mood_tag: e.target.value || null })}>
              <option value="">Any</option>
              {MOOD_TAGS.map(t => <option key={t}>{t}</option>)}
            </select>
          </div>
          <div className="field center">
            <label className="acoustic-label">
              <Toggle
                checked={profile.likes_acoustic}
                onChange={e => setProfile({ ...profile, likes_acoustic: e.target.checked })}
              />
              <span>Acoustic</span>
            </label>
          </div>
        </div>
      </div>

      {/* ── Add-ons ── */}
      <div className="addons-label">Optional Add-ons</div>

      {/* Describe */}
      <div className={`addon-card ${useQuery ? "addon-on" : ""}`}>
        <div className="addon-header" onClick={() => setUseQuery(v => !v)}>
          <span className="addon-title">✍️ Describe what you want</span>
          <Toggle checked={useQuery} onChange={e => setUseQuery(e.target.checked)} />
        </div>
        {useQuery && (
          <div className="addon-body">
            <textarea className="text-input"
              placeholder="e.g. Something upbeat to start my morning with good energy..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              rows={3}
            />
            <p className="hint">Gemini blends this with your profile above</p>
          </div>
        )}
      </div>

      {/* Songs I've heard */}
      <div className={`addon-card ${useSongs ? "addon-on" : ""}`}>
        <div className="addon-header" onClick={() => setUseSongs(v => !v)}>
          <span className="addon-title">🎧 Songs I've heard</span>
          <Toggle checked={useSongs} onChange={e => setUseSongs(e.target.checked)} />
        </div>
        {useSongs && (
          <div className="addon-body">
            <div className="tag-input-wrap">
              {songTags.map(t => (
                <span key={t} className="song-tag">
                  {t}<button className="tag-remove" onClick={() => removeTag(t)}>×</button>
                </span>
              ))}
              <input className="tag-input"
                placeholder={songTags.length ? "Add more..." : "e.g. Frank Ocean, Billie Eilish..."}
                value={songInput}
                onChange={e => setSongInput(e.target.value)}
                onKeyDown={addTag}
              />
            </div>
            <p className="hint">Press Enter or comma after each name — Gemini infers your taste from these</p>
          </div>
        )}
      </div>

      {/* ── Footer ── */}
      <div className="input-footer">
        <div className="mode-row">
          <label className="field-label" style={{ marginBottom: 0 }}>Scoring Mode</label>
          <select className="select-input compact" value={mode} onChange={e => setMode(e.target.value)}>
            {MODES.map(m => <option key={m} value={m}>{m.replace(/_/g, " ")}</option>)}
          </select>
        </div>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? <span className="spinner" /> : "Get Recommendations →"}
        </button>
      </div>
    </div>
  );
}
