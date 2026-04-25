import { useState } from "react";
import Header from "./components/Header";
import InputPanel from "./components/InputPanel";
import ResultsPanel from "./components/ResultsPanel";
import FeedbackDialog from "./components/FeedbackDialog";
import { recommend, recommendRetry } from "./services/api";
import "./App.css";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [prefs, setPrefs] = useState(null);
  const [diff, setDiff] = useState(null);

  const [feedbackState, setFeedbackState] = useState("idle"); // idle | asking | done
  const [lastQuery, setLastQuery] = useState("");
  const [retryLoading, setRetryLoading] = useState(false);
  const [retryDone, setRetryDone] = useState(false);

  async function handleSubmit({ profile, query, songs, mode }) {
    setLoading(true);
    setError(null);
    setResults(null);
    setWarnings([]);
    setPrefs(null);
    setDiff(null);
    setFeedbackState("idle");
    setRetryDone(false);

    // Build a human-readable description for the retry flow
    const parts = [];
    if (query) parts.push(query);
    if (songs?.length) parts.push(`songs: ${songs.join(", ")}`);
    setLastQuery(parts.join(" | ") || JSON.stringify(profile));

    try {
      const res = await recommend(profile, query, songs, mode);
      setResults(res.results);
      setWarnings(res.warnings ?? []);
      setPrefs(res.prefs);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRetry(feedback) {
    if (retryDone) return;
    setRetryLoading(true);
    setError(null);

    try {
      const res = await recommendRetry(lastQuery, feedback, prefs);
      setResults(res.results);
      setWarnings(res.warnings ?? []);
      setPrefs(res.prefs);
      setDiff(res.diff);
      setFeedbackState("done");
      setRetryDone(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setRetryLoading(false);
    }
  }

  function handleFeedback(answer) {
    if (answer === "yes") {
      setFeedbackState("done");
    } else {
      setFeedbackState("asking");
    }
  }

  return (
    <>
      <Header />
      <main className="main">
        <div className="content">
          <InputPanel onSubmit={handleSubmit} loading={loading} />

          {loading && (
            <div className="loading-block">
              <div className="loading-spinner" />
              <p>Finding your perfect songs<span className="dots" /></p>
            </div>
          )}

          {error && (
            <div className="error-block">
              <span>⚠</span> {error}
            </div>
          )}

          {results && !loading && (
            <>
              <ResultsPanel
                results={results}
                warnings={warnings}
                prefs={prefs}
                diff={diff}
                onFeedback={handleFeedback}
              />

              {feedbackState === "asking" && !retryDone && (
                <FeedbackDialog
                  onRetry={handleRetry}
                  onDismiss={() => setFeedbackState("done")}
                  loading={retryLoading}
                />
              )}

              {feedbackState === "done" && (
                <div className="done-block">
                  {retryDone ? "✦ Recommendations updated based on your feedback." : "✦ Glad these worked for you!"}
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </>
  );
}
