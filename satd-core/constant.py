import pandas as pd
from datasets import Dataset
from PromptTemplate import PromptTemplate
# Detection Dataset
DETECT_DATASET_NAME = 'duplicate'
detect_train_df = pd.read_csv(f'../data/{DETECT_DATASET_NAME}_detect_train.csv')
detect_train_dataset = Dataset.from_pandas(detect_train_df)

detect_test_df = pd.read_csv(f'../data/{DETECT_DATASET_NAME}_detect_test.csv')
detect_test_dataset = Dataset.from_pandas(detect_test_df)

detect_n_shot_df = pd.read_csv('../data/detect_n_shot.csv')
detect_n_shot_dataset = Dataset.from_pandas(detect_n_shot_df)
#Classification Dataset
classify_train_df = pd.read_csv(f'../data/{DETECT_DATASET_NAME}_classify_train.csv')
classify_train_dataset = Dataset.from_pandas(classify_train_df)

classify_test_df = pd.read_csv(f'../data/{DETECT_DATASET_NAME}_classify_test.csv')
classify_test_dataset = Dataset.from_pandas(classify_test_df)

classify_n_shot_df = pd.read_csv('../data/classify_n_shot.csv')
classify_n_shot_dataset = Dataset.from_pandas(classify_n_shot_df)
DEFAULT_DETECTION_CLASS = 'no'
DETECTION_TEMPLATE = PromptTemplate(
    name="Manually Crafted",
    definition="You are a Code Analysis Expert specialized in detecting Self-Admitted Technical Debt (SATD) in Java test code comments. SATD refers to comments where developers acknowledge that the current test implementation is incomplete, suboptimal, or relies on a compromise that should be addressed in the future. These admissions often appear as markers such as TODO or FIXME, or as notes about unresolved issues, temporary fixes, workarounds, hacks, performance limitations, use of deprecated APIs, unsupported features, poor design choices, skipped tests, or uncertain functionality. However, comments that only describe expected behavior, provide instructions, or reference external issues (e.g., JIRA ID) are not SATD unless there is additional information indicating the need for future improvement.",
    instruction="Think step by step and assign the label of **SATD** or **Not-SATD** for each given test code comment.",
    n_shot_template="Comment: {{ text }}",
    n_shot_answer_template="""{% if cot -%}
        Answer: {{ cot }} The answer is **{{ label }}**.
        {% endif -%}""",
    line_m_before=3,
    line_n_after=3
)