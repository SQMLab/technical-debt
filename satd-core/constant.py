import pandas as pd
from datasets import Dataset
from PromptTemplate import PromptTemplate
detect_train_df = pd.read_csv('../data/detect_train.csv')
detect_train_dataset = Dataset.from_pandas(detect_train_df)

detect_test_df = pd.read_csv('../data/detect_test.csv')
detect_test_dataset = Dataset.from_pandas(detect_test_df)

detect_n_shot_df = pd.read_csv('../data/detect_n_shot.csv')
detect_n_shot_dataset = Dataset.from_pandas(detect_n_shot_df)
DEFAULT_DETECTION_CLASS = 'no'
DETECT_DATASET_NAME = 'deduplicated test'
DETECTION_TEMPLATE = PromptTemplate(
    name="Manually Crafted",
    definition="You are Code Expert trained to detect Self-Admitted Technical Debt (SATD) in Java test code comments. SATD occurs when developers explicitly acknowledge that the current implementation is suboptimal, requires improvement, or contains technical compromises. These comments often include markers (e.g., TODO, FIXME), indicate unresolved issues, temporary fixes (e.g., workarounds, hacks), performance concerns, deprecated API usage, unsupported features, poor design, skipped tests, or unknown reasons. However, do not classify comments that merely describe expected behavior, actions, instructions or simply issue references, unless there is additional information indicating the need for future improvement. These comments often appear as imperative sentence structures (e.g., check argument, should not match), vague single-word description(e.g., clean up, retry, fail).",
    instruction="Classify by labelling it as 'yes' if the comment include a strong indication of Self-Admitted Technical Debt otherwise label it as 'no', do not return reason. Do not provide a reason for the classification.",
    n_shot_template="""
    <EXAMPLE>
    Comment: {{ text }}
    {% if cot -%}
    Reason: {{ cot }}
    {% endif -%}
    Label: {{ label }}
    </EXAMPLE>""",
    line_m_before=3,
    line_n_after=3
)