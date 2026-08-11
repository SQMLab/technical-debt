import argparse
import torch
import pandas as pd
from dotenv import load_dotenv
from accelerate import Accelerator
from datasets import Dataset
from HuggingFaceModel import HuggingFaceModel
from TrainStrategy import TrainStrategy
from constant import *
from LlmOutputLabelConverter import LlmOutputLabelConverter


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run SATD detection using a Hugging Face model."
    )

    parser.add_argument(
        "--template",
        required=True,
        help="Name of the prompt template.",
    )
    parser.add_argument(
        "--model-name",
        required=True,
        help="Hugging Face model name or path.",
    )
    parser.add_argument(
        "--dataset-name",
        required=True,
        help="Dataset name used when saving prediction results.",
    )
    parser.add_argument(
        "--shot",
        required=True,
        type=int,
        help="Number of examples to use for N-shot prompting.",
    )

    return parser.parse_args()

def main():
    args = parse_arguments()
    load_dotenv()
    accelerator = Accelerator()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    test_df = pd.read_csv(f'../data/{args.dataset_name}_detect_test.csv')
    test_dataset = Dataset.from_pandas(test_df)


    prompt_template = PromptTemplate(
        name=args.template,
        definition="You are a Code Analysis Expert specialized in detecting Self-Admitted Technical Debt (SATD) in Java test code comments. SATD refers to comments where developers acknowledge that the current test implementation is incomplete, suboptimal, or relies on a compromise that should be addressed in the future. These admissions often appear as markers such as TODO or FIXME, or as notes about unresolved issues, temporary fixes, workarounds, hacks, performance limitations, use of deprecated APIs, unsupported features, poor design choices, skipped tests, or uncertain functionality. However, comments that only describe expected behavior of test code are not SATD unless there is additional information indicating the need for future improvement.",
        instruction="Think step by step and assign the label of yes or no for each given test code comment.",
        n_shot_template='Comment: {{ text }}',
        n_shot_answer_template="Answer: {{ cot }} The answer is {{ label }}.",
        line_m_before=3,
        line_n_after=3)
    output_label_converter = LlmOutputLabelConverter({'yes', 'no'}, DEFAULT_DETECTION_CLASS)

    flan_t5_detection_model = HuggingFaceModel('detect',  args.model_name, output_label_converter, False)
    flan_t5_detection_model.fit(detect_n_shot_dataset)
    flan_t5_detection_model.predict(test_dataset, args.dataset_name, prompt_template, TrainStrategy.N_SHOT_TOP, args.shot, verbose=False)

if __name__ == "__main__":
    main()
