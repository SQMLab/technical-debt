import hashlib
import random
from sentence_transformers import SentenceTransformer, util
from TrainStrategy import TrainStrategy
import pandas as pd
import numpy as np
import os
from datasets import Dataset
from sklearn.metrics import classification_report
import sys
import jpype
sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')


def sha1(text):
    return hashlib.sha1(text.encode()).hexdigest()


def common_white_space_prefix_index(lines):
    filtered_lines = [line for line in lines if line != '\n']

    if len(filtered_lines) == 0:
        return 0
    min_length = min(len(line) for line in filtered_lines)

    common_prefix_length = 0
    while common_prefix_length < min_length and all(line[common_prefix_length].isspace() for line in filtered_lines):
        common_prefix_length += 1
    return common_prefix_length


def to_text_without_leading_common_whitespace(lines):
    common_prefix_length = common_white_space_prefix_index(lines)
    code_block = ''.join(line[common_prefix_length:] if common_prefix_length < len(line) else line for line in lines)
    if len(code_block) > 0 and code_block[-1] == '\n':
        return code_block[:-1]
    else:
        return code_block

def get_first_n_line(text, n):
    lines = text.split('\n') if text else []
    return '\n'.join(lines[:min(len(lines),n)])

def get_last_n_line(text, n):
    lines = text.split('\n') if text else []
    return '\n'.join(lines[max(0,len(lines) - n):])

def pick_n_shot(train_dataset: Dataset, test_dataset: Dataset, test_index: int, n: int = 0,
                strategy: TrainStrategy = None):
    dataset_length = train_dataset.num_rows
    if dataset_length < n:
        raise Exception(f'Train dataset contains only {dataset_length} examples for {n} shots')
    indexes = []
    if strategy == TrainStrategy.N_SHOT_RANDOM:
        indexes = random.sample(dataset_length, n)
    elif strategy == TrainStrategy.N_SHOT_SIMILAR:
        similarities = util.cos_sim(sentence_transformer.encode(test_dataset['text'][test_index]),
                                    sentence_transformer.encode(train_dataset['text'])).squeeze(0).numpy()
        top_n_indices = np.argpartition(similarities, -n)[-n:]
        indexes = top_n_indices[np.argsort(similarities[top_n_indices])[::-1]].tolist()
    elif strategy == TrainStrategy.N_SHOT_TOP:
        indexes = [i for i in range(n)]
    return indexes

def report_mismatch(input_file: str, merged_file: str, mismatched_file: str):
    last_df = pd.read_csv(input_file)
    for f in [merged_file, mismatched_file]:
        if not os.path.exists(merged_file):
            pd.DataFrame(columns=last_df.columns).to_csv(f, index=False)

    merged_df = pd.read_csv(merged_file)
    ids = merged_df['id'].values
    for index, row in last_df.iterrows():
        if row['id'] in ids:
            merged_df.loc[merged_df['id'] == row['id'], 'label_pred'] = row['label_pred']
        else:
            merged_df.loc[len(merged_df)] = row
    merged_df.sort_values(by=['id'], ascending=True, inplace=True)
    merged_df.to_csv(merged_file, index=False)
    merged_df[merged_df['label'] != merged_df['label_pred']].to_csv(mismatched_file, index=False)

def print_classification_excluding_outlier_repository(input_file: str, repository_id: int = 69):
    result_df = pd.read_csv(input_file)
    filtered_result_df = result_df[result_df['repository'] != repository_id]
    print(f'Test Result Excluding repository: {repository_id}')
    print(classification_report(filtered_result_df['label'], filtered_result_df['label_pred'], zero_division=0, digits=3))

def get_default_JVM_path():
    default_jvm_path = jpype.getDefaultJVMPath()
    # default_jvm_path_str = default_jvm_path.decode()
    # print(f"Default JVM path from JPype: {default_jvm_path}")
    # if sys.platform == "darwin":
    #     if not default_jvm_path_str.endswith("libjvm.dylib"):
    #         candidate = os.path.join(default_jvm_path_str, "lib", "server", "libjvm.dylib")
    #         # if os.path.exists(candidate):
    #         return candidate.encode()
    return default_jvm_path

def create_parent_directory(directories: list):
    for directory in directories:
        os.makedirs(os.path.dirname(directory), exist_ok=True)