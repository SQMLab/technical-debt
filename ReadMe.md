# 🧩 Replication Package: A First Look at the Self-Admitted Technical Debt (SATD) in Test Code

---

## 📖 Abstract

Self-Admitted Technical Debt (SATD) refers to comments in which developers explicitly acknowledge limitations, workarounds, or deferred improvements in code.  
While prior research has primarily focused on production code, this study presents the **first large-scale empirical investigation of SATD in test code**, introducing a taxonomy of 15 categories and evaluating both traditional detection tools and large language models (LLMs).

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

| Dataset                           | Description | File(s)                                                                                                                  |
|-----------------------------------|--------------|--------------------------------------------------------------------------------------------------------------------------|
| **All Extracted Comments**        | Full raw extracted comments (merged from line, block, and Javadoc) | [comment.zip](./data/comment.zip)                                                                                        |
| **Detection Sets (Original)**     | 80/20 split preserving natural duplication | [train.csv](./data/duplicate_detect_train.csv), [test.csv](./data/duplicate_detect_test.csv)                             |
| **Detection Sets (Deduplicated)** | 80/20 split after duplicate removal | [train.csv](./data/unique_detect_train.csv), [test.csv](./data/unique_detect_test.csv)                                   |
| **Labeled SATD Comments**         | Manually classified SATD | [satd comments.csv](./data/duplicate_satd_comment.csv), [deduplicated satd comments.csv](./data/unique_satd_comment.csv) |
| **Few-Shot Samples**              | Used for n-shot | [n-shots.csv](./data/detect_n_shot.csv)                                                                                  |

### 3. Dataset Summary
- Total comments: **47,994**  
- Projects: **488**  
- SATD comments: **615 (1.28%)**  
- Non-English comments excluded: **943**  
- Auto-generated comments excluded: **1,063**

---

## 🧰 Environment Setup

API tokens, directory paths, and runtime variables are managed through the environment configuration file:  
📄 [.env](./satd-core/.env)

### Prerequisites
- **Python** ≥ 3.10  
- **Java** ≥ 17  
- **Maven** ≥ 3.8  
- **CUDA-enabled GPU** recommended for LLM experiments

### Python Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---
## License
This project is licensed under the **MIT License**. For more information, see the [LICENSE](./LICENSE).