#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# get_ipython().run_line_magic('load_ext', 'autoreload')
# get_ipython().run_line_magic('autoreload', '2')
from dotenv import load_dotenv
from constant import *
from HuggingFaceModel import HuggingFaceModel
from TrainStrategy import TrainStrategy
from LlmOutputLabelConverter import LlmOutputLabelConverter
load_dotenv()

import argparse

parser = argparse.ArgumentParser(description="GPT OSS Config")
parser.add_argument(
    "--name",
    type=str,
    required=True,
    help="Model URI"
)
parser.add_argument(
    "--shot",
    type=int,
    required=True,
    help="How many shot(s)?"
)
args = parser.parse_args()
model_name = args.name
shot = args.shot
# In[ ]:


prompt_template = PromptTemplate(
    name="default",
    definition="You are a Code Analysis Expert specialized in detecting Self-Admitted Technical Debt (SATD) in Java test code comments. SATD refers to comments where developers acknowledge that the current test implementation is incomplete, suboptimal, or relies on a compromise that should be addressed in the future. These admissions often appear as markers such as TODO or FIXME, or as notes about unresolved issues, temporary fixes, workarounds, hacks, performance limitations, use of deprecated APIs, unsupported features, poor design choices, skipped tests, or uncertain functionality. However, comments that only describe expected behavior of test code are not SATD unless there is additional information indicating the need for future improvement.",
    instruction="Think step by step and assign the label of yes or no for each given test code comment.",
    n_shot_template='Comment: {{ text }}',
    n_shot_answer_template="Answer: {{ cot }} The answer is {{ label }}.",
    line_m_before=3,
    line_n_after=3)
output_label_converter = LlmOutputLabelConverter({'yes', 'no'}, DEFAULT_DETECTION_CLASS)
# MODELS = ['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'gpt-4o-mini', 'gpt-4o']


# # Sequential Request

# In[ ]:


gpt_model = HuggingFaceModel('detect', model_name, , True)
gpt_model.fit(detect_n_shot_dataset)
gpt_model.predict(detect_test_dataset, DATASET_NAME, prompt_template, TrainStrategy.N_SHOT_TOP, shot, verbose=False)


# # Dry Run

# In[ ]:


# for shots in [0]:
#     for model_name in ['openai/gpt-oss-20b']:
#         gpt_model = HuggingFaceModel('detect', model_name, output_label_converter, False)
#         gpt_model.fit(detect_n_shot_dataset)
#         gpt_model.predict(detect_test_dataset.select(range(1)), DATASET_NAME, prompt_template, TrainStrategy.N_SHOT_TOP, shots, verbose=True)
#
