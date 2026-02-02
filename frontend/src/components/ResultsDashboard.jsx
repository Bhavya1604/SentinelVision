import React from "react";
import styles from "./ResultsDashboard.module.css";

const VERDICT_STYLES = {
  SAFE: { class: styles.verdictSafe, label: "SAFE" },
  REVIEW: { class: styles.verdictReview, label: "REVIEW" },
  BLOCK: { class: styles.verdictBlock, label: "BLOCK" },
};

export function ResultsDashboard({ result, imagePreviewUrl }) {
  if (!result) return null;

  const { verdict, verdict_reason, categories, description } = result;
  const verdictStyle = VERDICT_STYLES[verdict] || VERDICT_STYLES.SAFE;

  return (
    <div className={styles.dashboard}>
      <div className={styles.grid}>
        <section className={styles.previewSection}>
          <h3 className={styles.sectionTitle}>Image</h3>
          {imagePreviewUrl ? (
            <img
              src={imagePreviewUrl}
              alt="Uploaded"
              className={styles.preview}
            />
          ) : (
            <div className={styles.previewPlaceholder}>No preview</div>
          )}
        </section>

        <section className={styles.verdictSection}>
          <h3 className={styles.sectionTitle}>Verdict</h3>
          <div className={`${styles.badge} ${verdictStyle.class}`}>
            {verdictStyle.label}
          </div>
          <p className={styles.reason}>{verdict_reason}</p>
        </section>
      </div>

      <section className={styles.categoriesSection}>
        <h3 className={styles.sectionTitle}>Confidence by category</h3>
        <ul className={styles.categoryList}>
          {categories.map((cat) => (
            <li key={cat.category} className={styles.categoryItem}>
              <div className={styles.categoryHeader}>
                <span className={styles.categoryLabel}>{cat.label}</span>
                <span className={styles.categoryValue}>
                  {(cat.score * 100).toFixed(1)}%
                </span>
              </div>
              <div className={styles.barTrack}>
                <div
                  className={styles.barFill}
                  style={{
                    width: `${cat.score * 100}%`,
                    backgroundColor:
                      cat.score >= 0.85
                        ? "var(--block)"
                        : cat.score >= 0.45
                          ? "var(--review)"
                          : "var(--safe)",
                  }}
                />
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className={styles.descriptionSection}>
        <h3 className={styles.sectionTitle}>Description (explainability)</h3>
        <p className={styles.description}>{description}</p>
      </section>
    </div>
  );
}
