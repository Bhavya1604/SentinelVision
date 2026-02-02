import React, { useCallback, useState } from "react";
import { ImageUpload } from "./components/ImageUpload";
import { ResultsDashboard } from "./components/ResultsDashboard";
import { analyzeImage } from "./api/client";
import styles from "./App.module.css";

export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = useCallback((selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setError(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(selectedFile));
  }, [previewUrl]);

  const analyze = useCallback(async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeImage(file);
      setResult(data);
    } catch (e) {
      setError(e.message || "Analysis failed.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, [file]);

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <h1 className={styles.title}>SentinelVision</h1>
        <p className={styles.subtitle}>Image moderation for Trust & Safety</p>
      </header>

      <main className={styles.main}>
        <section className={styles.uploadSection}>
          <ImageUpload
            onFileSelect={handleFileSelect}
            disabled={loading}
          />
          <div className={styles.actions}>
            <button
              type="button"
              className={styles.analyzeBtn}
              onClick={analyze}
              disabled={!file || loading}
            >
              {loading ? "Analyzing…" : "Analyze"}
            </button>
          </div>
          {error && <p className={styles.error}>{error}</p>}
        </section>

        {result && (
          <section className={styles.resultsSection}>
            <ResultsDashboard result={result} imagePreviewUrl={previewUrl} />
          </section>
        )}
      </main>

      <footer className={styles.footer}>
        <span>SentinelVision</span>
        <span className={styles.footerMuted}>Multi-label moderation · Explainability</span>
      </footer>
    </div>
  );
}
