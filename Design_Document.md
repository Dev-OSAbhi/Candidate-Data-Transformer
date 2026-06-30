# Technical Design: Multi-Source Candidate Data Transformer

## 1. Pipeline Architecture
The system is divided into isolated, testable modules enforcing a unidirectional data flow:
1. **Extractors (`engine/extractors.py`):** Ingests raw files (CSV, JSON, TXT). Maps diverse schemas into a standardized `RawRecord` dictionary. Unstructured text uses targeted regex heuristics to surface entities.
2. **Normalizers (`engine/normalizers.py`):** Pure functions that standardize data types (e.g., E.164 for phones, ISO-8601 YYYY-MM for dates, lowercase-stripped for canonical skills).
3. **Merger (`engine/merger.py`):** - *Identity Resolution:* Uses exact email matching to group records belonging to the same candidate.
   - *Conflict Resolution:* Field-level merging based on source confidence (Structured ATS = 0.9, CSV = 0.8, Unstructured TXT = 0.6). High-confidence sources overwrite low-confidence ones for scalar values (like names). Arrays (skills, emails) are deduplicated and unioned.
4. **Projector (`engine/projector.py`):** The "Twist". A dynamic JSON projection layer that reshapes the canonical record based on runtime configurations without altering core engine logic.

## 2. Canonical Output Schema & Normalization
* **Dates:** Parsed from varied strings into `YYYY-MM`.
* **Phones:** Non-numeric characters stripped. Assumes `+1` if exactly 10 digits; outputs E.164.
* **Skills:** Converted to lowercase, stripped of bounding punctuation to allow grouping of "Python," and "python".
* **Locations:** Mapped to ISO-3166 alpha-2 if a known country string is detected.

## 3. Merge Policy & Confidence Tracking
* **Winning Values:** For single-value fields (e.g., `full_name`, `headline`), the value from the highest-confidence source is retained. 
* **Array Unioning:** Skills track multiple sources. If "Python" is found in CSV (0.8) and TXT (0.6), the canonical skill entry keeps the highest confidence (0.8) and appends both sources to its `sources[]` array.
* **Provenance:** Every update to the canonical profile appends a `{ field, source, method }` dict to the provenance array, maintaining 100% auditability.
* **Overall Confidence:** Calculated as the average confidence of all populated, top-level scalar and array fields.

## 4. Runtime Configuration (The Twist)
The projection engine uses a dot-notation parser (e.g., `emails[0]`) to traverse the canonical dictionary. 
* It iterates through the config's `fields` array.
* Fetches data using the `from` path (defaults to `path` if absent).
* Applies late-stage normalizations if requested.
* Handles missing data based on `on_missing`: `null` outputs `None`, `omit` skips the key, and `error` raises a fatal exception to fail fast.

## 5. Edge Cases Handled
* **Garbage Text/Missing Keys:** Extractors wrap operations in `try/except` and safely return `None`, preventing pipeline crashes.
* **Orphan Records:** If a source lacks an email for identity resolution, a deterministic UUID is hashed from the payload to ensure consistent processing without collision.