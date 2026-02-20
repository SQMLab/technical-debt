from abc import abstractmethod
from datasets import Dataset
from sklearn.metrics import classification_report
import os
from datetime import datetime
from util import report_mismatch
import PromptTemplate
import pandas as pd
from OutputLabelConverter import OutputLabelConverter
from sklearn.metrics import roc_auc_score
from sklearn.metrics import matthews_corrcoef

import random
from datasets.utils.logging import set_verbosity, disable_progress_bar, enable_progress_bar

N_SHOT_PROPERTIES = ['text', 'label', 'code_before', 'code_after', 'cot']


class Model:
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter,
                 cache_update_batch_size: int, enable_cache: bool = False):
        self.task_type = task_type
        self.model_uri = model_uri
        self.output_label_converter = output_label_converter
        self.unknown_labels = []
        self.enable_cache = enable_cache
        self.cache_update_batch_size = cache_update_batch_size
        self.cache_raw_label = {}

    @abstractmethod
    def fit(self, dataset: Dataset):
        pass

    @abstractmethod
    def predict(self, dataset: Dataset):
        pass

    def format_label(self, label, verbose: bool = False):
        formatted_label = label.lower()
        for key in [':', '**', '.', 'answer', 'label']:
            formatted_label = formatted_label.replace(key, '')
        formatted_label = formatted_label.strip()
        if formatted_label in self.output_label_converter.known_labels:
            return formatted_label
        else:
            if verbose:
                print(f'Unknown Label: {label}')
            self.unknown_labels.append(label)
            return self.output_label_converter.unmatched_label

    def predict_start(self, dataset: Dataset, model_name_suffix: str = None):
        print(f'{self.get_full_model_name(model_name_suffix)}')
        self.unknown_labels.clear()

    def predict_end(self, dataset: Dataset, dataset_name, label_predictions, raw_label_predictions,
                    model_name_suffix: str = None, label_probabilities: list = None):
        full_model_name = self.get_full_model_name(model_name_suffix)
        output_file_name = self.get_output_file_name(full_model_name)
        timestamp = datetime.now().strftime("%B %d, %Y, %H:%M:%S")
        file = f'{self.get_base_output_directory()}/snapshot/{timestamp}${output_file_name}'
        os.makedirs(os.path.dirname(file), exist_ok=True)
        merged_file = self.get_merged_file(model_name_suffix)
        mismatched_file = f'{self.get_base_output_directory()}/mismatched/mismatched_{output_file_name}'
        os.makedirs(os.path.dirname(mismatched_file), exist_ok=True)

        if self.unknown_labels:
            print(f'Unknown Labels:\n{self.unknown_labels}')
        print('Test Result:')
        print(classification_report(dataset['label'], label_predictions, zero_division=0, digits=3, output_dict=False))
        report_dict = classification_report(dataset['label'], label_predictions, zero_division=0, digits=3,
                                            output_dict=True)
        rows = []
        total_support = int(report_dict['macro avg']['support'])
        for metric, values in report_dict.items():
            if metric == "accuracy":
                row = {
                    "metric": metric,
                    "precision": None,
                    "recall": None,
                    "f1-score": round(values, 3),
                    "support": total_support
                }
            else:
                row = {
                    "metric": metric,
                    "precision": round(values.get("precision", 0), 3),
                    "recall": round(values.get("recall", 0), 3),
                    "f1-score": round(values.get("f1-score", 0), 3),
                    "support": int(values.get("support", 0))
                }
            if metric == "yes":
                row["mcc"] =  round(matthews_corrcoef(self.label_to_probability(dataset['label']),self.label_to_probability(label_predictions)), 3)
                if label_probabilities:
                    row["auc"] = round(roc_auc_score(self.label_to_probability(dataset['label']), label_probabilities), 3)
                else:
                    row["auc"] = None
            else:
                row["mcc"] = None
                row["auc"] = None

            row["model"] = full_model_name
            row["dataset"] = dataset_name
            rows.append(row)

        report_df = pd.DataFrame(rows)
        report_df = report_df[["model", "dataset", "metric", "precision", "recall", "f1-score", "mcc", "auc", "support"]]
        output_metrics_file = f'{self.get_base_output_directory()}/{self.task_type}_output_metrics.csv'
        os.makedirs(os.path.dirname(output_metrics_file), exist_ok=True)
        if os.path.exists(output_metrics_file):
            output_metric_df = pd.read_csv(output_metrics_file)
            output_metric_df = output_metric_df[
                ~((output_metric_df["model"] == full_model_name) &
                  (output_metric_df["dataset"] == dataset_name))
            ]
            pd.concat([output_metric_df, report_df], ignore_index=True).to_csv(output_metrics_file, index=False)
        else:
            report_df.to_csv(output_metrics_file, index=False)
        self.panda_dataframe_result(dataset, label_predictions, raw_label_predictions).to_csv(file, index=False)
        report_mismatch(file, merged_file, mismatched_file)

        return file

    def project_properties(self, dataset: Dataset, index: int):
        properties = {}
        for key in N_SHOT_PROPERTIES:
            if key in dataset.features.keys():
                properties[key] = dataset[key][index]

        return properties

    def create_input(self, prompt_template: PromptTemplate, train_dataset: Dataset, train_indexes,
                     test_dataset: Dataset,
                     test_index: int, verbose: bool = False):
        message = []
        isGpt = 'gpt' in self.model_uri
        isGemini = 'gemini' in self.model_uri

        for index in train_indexes:
            input_example = prompt_template.create_example(self.project_properties(train_dataset, index))
            input_answer = prompt_template.create_answer(self.project_properties(train_dataset, index))

            if isGpt:
                message.append({'role': 'user', 'content': input_example})
                message.append({'role': 'developer', 'content': input_answer})
            elif isGemini:
                message.append({
                    'parts': [{'text': input_example}],
                    'role': 'user'
                })
                message.append({
                    'parts': [{'text': input_answer}],
                    'role': 'model'
                })
                # message.append(f'<EXAMPLE>\n{input_example}\n{input_answer}\n</EXAMPLE>')
            else:
                message.append(f'{input_example}\n{input_answer}')

        test_properties = self.project_properties(test_dataset, test_index)
        if 'label' in test_properties:
            test_properties['label'] = ''
        input_question = prompt_template.create_example(test_properties)
        whole_question_part = f'{input_question}\n{prompt_template.create_answer(test_properties)}' if prompt_template.add_question_label else f'{input_question}'

        if isGpt:
            message.append({'role': 'user', 'content': input_question})
        elif isGemini:
            message.append({
                'parts': [{'text': input_question}],
                'role': 'user'
            })
        else:
            message.append(whole_question_part)

        if isGpt or isGemini:
            prompt = message
        else:
            prompt = "\n".join(message)
        if verbose:
            print(f'{prompt}')
        return prompt

    def get_full_model_name(self, model_name_suffix):
        return self.model_uri + f'-{model_name_suffix}' if model_name_suffix else self.model_uri

    def get_output_file_name(self, model_name_suffix):
        return f'{self.task_type}_{self.get_full_model_name(model_name_suffix).split("/")[-1]}.csv'

    def add_into_batch_job(self, input_file, job_id, job_name, count, status):
        job_file = f'{os.getenv("CACHE_DIRECTORY")}/output/batch/job.csv'
        os.makedirs(os.path.dirname(job_file), exist_ok=True)
        job_df = pd.read_csv(job_file) if os.path.exists(job_file) else pd.DataFrame()
        new_row = pd.DataFrame([{
            "model_uri": self.model_uri,
            "task_type": self.task_type,
            "input_file": input_file,
            "job_id": job_id,
            "job_name": job_name,
            "count": count,
            "status": status,
            "created_at": pd.Timestamp.now(),
            "updated_at": pd.Timestamp.now()
        }])
        job_df = pd.concat([job_df, new_row], ignore_index=True)
        job_df.to_csv(job_file, index=False)

    def create_batch_input_file_name(self, model_name_suffix):
        batch_input_file = f'{self.get_base_output_directory()}/batch/input/{self.task_type}_{self.get_full_model_name(model_name_suffix).split("/")[-1]}.jsonl'
        os.makedirs(os.path.dirname(batch_input_file), exist_ok=True)
        return batch_input_file

    def get_merged_file(self, model_name_suffix):
        merged_file = f'{self.get_base_output_directory()}/merged/merged_{self.get_output_file_name(model_name_suffix)}'
        os.makedirs(os.path.dirname(merged_file), exist_ok=True)
        return merged_file

    def get_base_output_directory(self):
        return f'{os.getenv("CACHE_DIRECTORY")}/output'

    def load_raw_label_if_needed(self, merged_file, reload : bool = False):
        if reload or  merged_file not in self.cache_raw_label:
            if os.path.exists(merged_file):
                df = pd.read_csv(merged_file)
                self.cache_raw_label[merged_file] = dict(zip(df['hash'], df['label_pred_raw']))

    def read_from_merged_file(self, model_name_suffix, text_hash):
        merged_file = self.get_merged_file(model_name_suffix)
        self.load_raw_label_if_needed(merged_file, reload=False)
        if merged_file in self.cache_raw_label and text_hash in self.cache_raw_label[merged_file]:
            return self.cache_raw_label[merged_file][text_hash]
        return None

    def panda_dataframe_result(self, dataset: Dataset, label_predictions, raw_label_predictions):
        test_output = dataset.to_dict()
        test_output['label_pred'] = label_predictions
        test_output['label_pred_raw'] = raw_label_predictions
        # Avoid empty string to NaN conversion issue in pandas
        # cleaned = {k: ["" if pd.isna(x) else str(x) for x in v] for k, v in test_output.items()}
        # return Dataset.from_dict(cleaned).to_pandas()
        return Dataset.from_dict(test_output).to_pandas()

    def append_into_merged_file(self, model_name_suffix, dataset, ids, predicted_labels, raw_predicted_labels):
        id_map = dict(zip(ids, list(zip(predicted_labels, raw_predicted_labels))))
        common_rows = []
        common_predicted_labels = []
        common_raw_predicted_labels = []
        for row in dataset:
            if row['id'] in id_map:
                common_rows.append(row)
                common_predicted_labels.append(id_map[row['id']][0])
                common_raw_predicted_labels.append(id_map[row['id']][1])
        if len(common_rows) < len(ids):
            print('warning .. updating {len(common_rows)} / {len(ids)}')
        new_result_df = self.panda_dataframe_result(Dataset.from_list(common_rows), common_predicted_labels,
                                                    common_raw_predicted_labels)
        merged_file = self.get_merged_file(model_name_suffix)
        if os.path.exists(merged_file):
            df = pd.read_csv(merged_file)
            df = df[~df['id'].isin(set(new_result_df['id']))]
            pd.concat([df, new_result_df], ignore_index=True).to_csv(merged_file, index=False)
        else:
            new_result_df.to_csv(merged_file, index=False)
        self.load_raw_label_if_needed(merged_file, reload=True)
        return None

    def create_model_suffix(self, prompt_template: PromptTemplate, n_shot_size: int = None):
        if len(prompt_template.name) > 0:
            return f'{prompt_template.name}-{n_shot_size}-shot'
        else:
            return f'{n_shot_size}-shot'

    def label_to_probability(self, labels):
        return [1 if x.lower() == "yes" else 0 for x in labels]

    def inject_mcc_auc(self, dataset: Dataset, dataset_name, label_predictions, raw_label_predictions,
                    full_model_name: str = None, label_probabilities: list = None):

        report_dict = classification_report(dataset['label'], label_predictions, zero_division=0, digits=3,
                                            output_dict=True)
        rows = []
        total_support = int(report_dict['macro avg']['support'])
        for metric, values in report_dict.items():
            if metric == "accuracy":
                row = {
                    "metric": metric,
                    "precision": None,
                    "recall": None,
                    "f1-score": round(values, 3),
                    "support": total_support
                }
            else:
                row = {
                    "metric": metric,
                    "precision": round(values.get("precision", 0), 3),
                    "recall": round(values.get("recall", 0), 3),
                    "f1-score": round(values.get("f1-score", 0), 3),
                    "support": int(values.get("support", 0))
                }
            if metric == "yes":
                row["mcc"] =  round(matthews_corrcoef(self.label_to_probability(dataset['label']),self.label_to_probability(label_predictions)), 3)
                if label_probabilities:
                    row["auc"] = round(roc_auc_score(self.label_to_probability(dataset['label']), label_probabilities), 3)
                else:
                    row["auc"] = None
            else:
                row["mcc"] = None
                row["auc"] = None

            row["model"] = full_model_name
            row["dataset"] = dataset_name
            rows.append(row)

        report_df = pd.DataFrame(rows)
        report_df = report_df[["model", "dataset", "metric", "precision", "recall", "f1-score", "mcc", "auc", "support"]]
        output_metrics_file = f'{self.get_base_output_directory()}/{self.task_type}_output_metrics.csv'
        os.makedirs(os.path.dirname(output_metrics_file), exist_ok=True)
        if os.path.exists(output_metrics_file):
            output_metric_df = pd.read_csv(output_metrics_file)
            output_metric_df = output_metric_df[
                ~((output_metric_df["model"] == full_model_name) &
                  (output_metric_df["dataset"] == dataset_name))
            ]
            pd.concat([output_metric_df, report_df], ignore_index=True).to_csv(output_metrics_file, index=False)
        else:
            report_df.to_csv(output_metrics_file, index=False)