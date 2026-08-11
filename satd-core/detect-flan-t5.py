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
from SatdToYesNoConverter import SatdToYesNoConverter


PROMPT_NAMES = ("default", "definition", "mat", "jitterbug", "gpt")


def positive_integer(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("run index must be greater than or equal to 1")
    return value


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run SATD detection using a Hugging Face model."
    )

    parser.add_argument(
        "--prompt-name",
        required=True,
        choices=PROMPT_NAMES,
        help="Prompt template to use.",
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
    parser.add_argument(
        "--run-index",
        type=positive_integer,
        default=1,
        help="One-based repetition index; indexes from 2 are added to the output name.",
    )

    return parser.parse_args()


def resolve_prompt_name(prompt_name, run_index):
    if run_index >= 2:
        return f"{prompt_name}{run_index}"
    return prompt_name


def resolve_prompt(prompt_name, run_index):
    resolved_name = resolve_prompt_name(prompt_name, run_index)

    if prompt_name == "default":
        prompt_template = PromptTemplate(
            name=resolved_name,
            definition="You are a Code Analysis Expert specialized in detecting Self-Admitted Technical Debt (SATD) in Java test code comments. SATD refers to comments where developers acknowledge that the current test implementation is incomplete, suboptimal, or relies on a compromise that should be addressed in the future. These admissions often appear as markers such as TODO or FIXME, or as notes about unresolved issues, temporary fixes, workarounds, hacks, performance limitations, use of deprecated APIs, unsupported features, poor design choices, skipped tests, or uncertain functionality. However, comments that only describe expected behavior of test code are not SATD unless there is additional information indicating the need for future improvement.",
            instruction="Think step by step and assign the label of yes or no for each given test code comment.",
            n_shot_template='Comment: {{ text }}',
            n_shot_answer_template="Answer: {{ cot }} The answer is {{ label }}.",
            line_m_before=3,
            line_n_after=3,
        )
        output_label_converter = LlmOutputLabelConverter(
            {'yes', 'no'}, DEFAULT_DETECTION_CLASS
        )
        return prompt_template, output_label_converter, detect_n_shot_dataset

    definitions = {
        "definition": "Self-admitted technical debt (SATD) is technical debt admitted by the developer through source code comments.",
        "mat": "Self-admitted technical debt (SATD) is technical debt admitted by the developer through source code comments. SATD comments usually contains specific keywords: TODO, FIXME, HACK, and XXX.",
        "jitterbug": "Self-admitted technical debt (SATD) is technical debt admitted by the developer through source code comments. SATD comments usually contains specific keywords: TODO, FIXME, HACK, and WORKAROUND.",
        "gpt": "Self-admitted technical debt (SATD) is technical debt admitted by the developer through source code comments. SATD comments usually contains specific keywords: TODO, FIXME, HACK, XXX, NOTE, DEBT, REFACTOR, OPTIMIZE, TEMP, WORKAROUND, KLUDGE, REVIEW, NOFIX, PENDING, and BUG.",
    }
    prompt_template = PromptTemplate(
        name=resolved_name,
        definition=definitions[prompt_name],
        instruction="Assign the label of SATD or Not-SATD for each given source code comment.\n\nHere are some examples:",
        n_shot_template='### Comment text: """ {{ text }} """',
        n_shot_answer_template="### Label: {{ label }}\n\n",
        line_m_before=0,
        line_n_after=0,
        add_question_label=True,
    )
    output_label_converter = SatdToYesNoConverter(LlmOutputLabelConverter({'SATD', 'Not-SATD'}, 'Not-SATD'))
    shots_df = detect_n_shot_df.copy(deep=True)
    shots_df['label'] = shots_df['label'].map({'yes': 'SATD', 'no': 'Not-SATD'})
    shots_dataset = Dataset.from_pandas(shots_df)
    return prompt_template, output_label_converter, shots_dataset

def main():
    args = parse_arguments()
    load_dotenv()
    accelerator = Accelerator()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    test_df = pd.read_csv(f'../data/{args.dataset_name}_detect_test.csv')
    test_dataset = Dataset.from_pandas(test_df)


    prompt_template, output_label_converter, shots_dataset = resolve_prompt(
        args.prompt_name, args.run_index
    )

    flan_t5_detection_model = HuggingFaceModel('detect',  args.model_name, output_label_converter, False)
    flan_t5_detection_model.fit(shots_dataset)
    flan_t5_detection_model.predict(test_dataset, args.dataset_name, prompt_template, TrainStrategy.N_SHOT_TOP, args.shot, verbose=False)

if __name__ == "__main__":
    main()
