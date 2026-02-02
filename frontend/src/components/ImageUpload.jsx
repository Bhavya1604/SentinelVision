import React, { useCallback, useRef, useState } from "react";
import styles from "./ImageUpload.module.css";

const ACCEPT = "image/jpeg,image/png,image/webp";
const MAX_MB = 10;

export function ImageUpload({ onFileSelect, disabled }) {
  const [drag, setDrag] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const validate = useCallback((file) => {
    if (!file.type.match(/^image\/(jpeg|png|webp)$/)) {
      return "Please use JPEG, PNG, or WebP.";
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      return `File must be under ${MAX_MB} MB.`;
    }
    return null;
  }, []);

  const handleFile = useCallback(
    (file) => {
      setError(null);
      const err = validate(file);
      if (err) {
        setError(err);
        return;
      }
      onFileSelect(file);
    },
    [onFileSelect, validate]
  );

  const onDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDrag(false);
      const file = e.dataTransfer?.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onDragOver = useCallback((e) => {
    e.preventDefault();
    setDrag(true);
  }, []);

  const onDragLeave = useCallback((e) => {
    e.preventDefault();
    setDrag(false);
  }, []);

  const onInputChange = useCallback(
    (e) => {
      const file = e.target?.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const openPicker = useCallback(() => {
    if (disabled) return;
    inputRef.current?.click();
  }, [disabled]);

  return (
    <div
      className={`${styles.zone} ${drag ? styles.drag : ""} ${disabled ? styles.disabled : ""}`}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onClick={openPicker}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && openPicker()}
      aria-label="Upload image by click or drag and drop"
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        onChange={onInputChange}
        className={styles.input}
        aria-hidden
      />
      <span className={styles.icon}>↑</span>
      <span className={styles.text}>
        Drag & drop an image here, or click to browse
      </span>
      <span className={styles.hint}>JPEG, PNG or WebP · max {MAX_MB} MB</span>
      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
}
