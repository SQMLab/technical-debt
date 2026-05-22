
# 🧩 Replication Package: A First Look at the Self-Admitted Technical Debt in Test Code: Taxonomy and Detection

---

## 📖 Abstract

Self-Admitted Technical Debt (SATD) refers to comments in which developers explicitly acknowledge limitations, workarounds, or deferred improvements in code.  
While prior research has primarily focused on production code, this study presents the **first large-scale empirical investigation of SATD in test code**, introducing a taxonomy of 14 categories and evaluating both traditional approaches and large language models (LLMs).

---

## 🧠 Research Questions

| RQ | Description | Related Files |
|----|--------------|---------------|
| **RQ1** | What types of SATD appear in test code? | [satd-core/manual_classification.py](./satd-core/manual_classification.py) |
| **RQ2** | Can existing SATD detection tools identify SATD in test code? | [satd-core/detect-mat.ipynb](./satd-core/detect-mat.ipynb) |
| **RQ3** | Can open-source LLMs (e.g., Flan-T5) detect SATD in test code? | [satd-core/detect-flan-t5.ipynb](./satd-core/detect-flan-t5.ipynb), [satd-core/detect-sadegh-flan-t5.ipynb](./satd-core/detect-sadegh-flan-t5.ipynb) |
| **RQ4** | Can proprietary LLMs (e.g., GPT, Gemini) detect SATD in test code? | [satd-core/detect-gpt.ipynb](./satd-core/detect-gpt.ipynb), [satd-core/detect-gemini.ipynb](./satd-core/detect-gemini.ipynb) |

---

## 🗂️ Dataset Description

### 1. Repository Metadata
- **File:** [repository.csv](./data/repository.csv)  
- **Description:** Metadata of 1,000 open-source Java repositories collected from GitHub, including repository URLs, stars, and size.

### 2. Comment Data

| Dataset                           | Description | File(s) |
|-----------------------------------|--------------|---------|
| **All Extracted Comments**        | Full raw extracted comments (merged from line, block, and Javadoc) | [comment.zip](./data/comment.zip) |
| **Detection Sets (Original)**     | 80/20 split preserving natural duplication | [train.csv](./data/duplicate_detect_train.csv), [test.csv](./data/duplicate_detect_test.csv) |
| **Detection Sets (Deduplicated)** | 80/20 split after duplicate removal | [train.csv](./data/unique_detect_train.csv), [test.csv](./data/unique_detect_test.csv) |
| **Labeled SATD Comments**         | Manually classified SATD | [satd comments.csv](./data/duplicate_satd_comment.csv), [deduplicated satd comments.csv](./data/unique_satd_comment.csv) |
| **Few-Shot Samples**              | Used for n-shot prompting | [n-shots.csv](./data/detect_n_shot.csv) |

### 3. Dataset Summary
- Total comments: **47,994**
- Projects: **488**
- SATD comments: **615 (1.28%)**
- Non-English comments excluded: **943**
- Auto-generated comments excluded: **1,063**

---

# 📊 Experimental Results

All experiment outputs are stored in the **`result/`** directory.  
Each research question has a dedicated folder containing the prediction outputs and evaluation metrics.

```
result/
 ├── rq2/
 ├── rq3/
 └── rq4/
```

---

## RQ2 – Existing SATD Detection Approaches

RQ2 evaluates **existing SATD detection approaches** on SATD comments extracted from test code.

```
result/rq2/
 ├── duplicate/
 └── unique/
```

- **duplicate/** – experiments using the original dataset where duplicated comments are preserved.
- **unique/** – experiments after removing duplicate comments.

Evaluated tools include:

- Pattern-based detector (Potdar)
- MAT
- NLP-based detector
- Text Mining (TM)
- Liu detector
- BERT-based classifier
- DebtHunter

Example result files:

```
detect_pretrained-MAT.csv
detect_pretrained-potdar-Pattern.csv
detect_pretrained-NLP.csv
detect_pretrained-TM.csv
detect_pretrained-liu-detector.csv
detect_pretrained-bert-default.csv
```

Retrained model results are also provided:

```
detect_trained-bert-default.csv
detect_trained-liu-detector.csv
```

For BERT and Liu detectors, **5-fold cross-validation results** are included:

```
detect_trained-bert-5fcv-1.csv
detect_trained-bert-5fcv-2.csv
detect_trained-bert-5fcv-3.csv
detect_trained-bert-5fcv-4.csv
detect_trained-bert-5fcv-5.csv
```

---

## RQ3 – Open-Source LLMs

RQ3 evaluates **open-source large language models** for SATD detection in test code.

```
result/rq3/
 ├── duplicate/
 └── unique/
```

These experiments correspond to:

- `satd-core/detect-flan-t5.ipynb`
- `satd-core/detect-sadegh-flan-t5.ipynb`

Each CSV file contains:

- predicted labels
- ground truth labels

---

## RQ4 – Proprietary LLMs

RQ4 evaluates **commercial LLMs** including GPT and Gemini models.

```
result/rq4/
 ├── duplicate/
 └── unique/
```

Each file corresponds to classification result for a specific configuration.

Example GPT results:

```
detect_gpt-5-0-shot.csv
detect_gpt-5-2-shot.csv
detect_gpt-5-4-shot.csv
```

Example Gemini results:

```
detect_gemini-2.0-flash-0-shot.csv
detect_gemini-2.0-flash-2-shot.csv
detect_gemini-2.0-flash-4-shot.csv
detect_gemini-2.5-flash-0-shot.csv
detect_gemini-2.5-flash-2-shot.csv
detect_gemini-2.5-flash-4-shot.csv
```

Model variants evaluated:

- GPT‑5
- GPT‑5‑mini
- GPT‑5‑nano
- Gemini‑2.0‑flash
- Gemini‑2.5‑flash

Prompting configurations:

- **0-shot**
- **2-shot**
- **4-shot**

---

## 🧰 Environment Setup

API tokens, directory paths, and runtime variables are managed through the environment configuration file:  
`.env` located in:

```
satd-core/.env
```

### Prerequisites

- **Python ≥ 3.10**
- **Java ≥ 17**
- **Maven ≥ 3.8**
- **CUDA-enabled GPU** recommended for LLM experiments

### Python Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](./LICENSE) file for details.