import { useState } from "react";
import "./FeedbackDialog.css";

export default function FeedbackDialog({ onRetry, onDismiss, loading }) {
  const [feedback, setFeedback] = useState("");

  function handleRetry() {
    if (!feedback.trim()) return;
    onRetry(feedback.trim());
  }

  return (
    <div className="feedback-dialog">
      <div className="feedback-header">
        <span className="feedback-icon">💬</span>
        <div>
          <p className="feedback-title">What didn't you like?</p>
          <p className="feedback-sub">Tell us why and we'll adjust the recommendations.</p>
        </div>
      </div>

      <textarea
        className="feedback-input"
        placeholder="e.g. Too high energy, I wanted something slower and more relaxed..."
        value={feedback}
        onChange={e => setFeedback(e.target.value)}
        rows={3}
      />

      <div className="feedback-actions">
        <button className="btn-dismiss" onClick={onDismiss} disabled={loading}>
          Never mind
        </button>
        <button
          className="btn-retry"
          onClick={handleRetry}
          disabled={loading || !feedback.trim()}
        >
          {loading ? <span className="spinner" /> : "🔄 Retry with feedback"}
        </button>
      </div>
    </div>
  );
}
