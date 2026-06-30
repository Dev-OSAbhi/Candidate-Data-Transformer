# Multi-Source Candidate Data Transformer

A deterministic pipeline that ingests candidate data from heterogeneous structured and unstructured sources, normalizes it, merges it into a highly trustworthy canonical profile, and projects it via a dynamic configuration schema.

## Architecture Highlights
* **Modular Design:** Divided into `extractors`, `normalizers`, `merger`, and `projector`.
* **Zero Dependencies:** Written purely in Python Standard Library to ensure robustness and ease of deployment.
* **Deterministic Resolution:** Uses exact email matching and source-confidence weighting to solve data conflicts.
* **Graceful Degradation:** Malformed inputs bypass cleanly without crashing the overarching batch pipeline.

## Prerequisites
* Python 3.8+ (No `pip install` required)

## Usage

**1. Run with Default Canonical Schema:**
Point the CLI to your data sources. It will ingest, deduplicate, merge, and print the raw canonical JSON.
```bash
python main.py --csv sample.csv --ats sample_ats.json --txt sample.txt