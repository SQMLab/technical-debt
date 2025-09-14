from abc import abstractmethod
from datasets import Dataset
from sklearn.metrics import classification_report
import os
from datetime import datetime
from util import report_mismatch
import PromptTemplate
import pandas as pd
from OutputLabelConverter import OutputLabelConverter

N_SHOT_PROPERTIES = ['text', 'label', 'code_before', 'code_after', 'cot']


class Model:
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter):
        self.task_type = task_type
        self.model_uri = model_uri
        self.output_label_converter = output_label_converter
        self.unknown_labels = []

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

    def predict_start(self, dataset: Dataset):
        print(f'{self.task_type} with {self.model_uri.split("/")[-1]}')
        self.unknown_labels.clear()

    def predict_end(self, dataset: Dataset, dataset_name, label_predictions, raw_label_predictions, model_name_suffix: str = None):
        full_model_name = self.model_uri + f'-{model_name_suffix}' if model_name_suffix else self.model_uri
        file_name = f'{self.task_type}_{full_model_name.split("/")[-1]}'
        test_output = dataset.to_dict()
        test_output['label_pred'] = label_predictions
        test_output['label_pred_raw'] = raw_label_predictions
        if self.unknown_labels:
            print(f'Unknown Labels:\n{self.unknown_labels}')
        timestamp = datetime.now().strftime("%B %d, %Y, %H:%M:%S")
        cache_directory = os.getenv("CACHE_DIRECTORY")
        file = f'{cache_directory}/output/tmp/{timestamp}${file_name}.csv'
        os.makedirs(os.path.dirname(file), exist_ok=True)
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
            row["model"] = full_model_name
            row["dataset"] = dataset_name
            rows.append(row)

        report_df = pd.DataFrame(rows)
        report_df = report_df[["model", "dataset", "metric", "precision", "recall", "f1-score", "support"]]
        output_metrics_file = f'{cache_directory}/output/output_metrics.csv'
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

        Dataset.from_dict(test_output).to_pandas().to_csv(file, index=False)
        report_mismatch(file)

        return file

    def project_properties(self, dataset: Dataset, index: int):
        properties = {}
        for key in N_SHOT_PROPERTIES:
            if key in dataset.features.keys():
                properties[key] = dataset[key][index]
        return properties

    def create_prompt(self, prompt_template: PromptTemplate, train_dataset: Dataset, train_indexes: [int],
                      test_dataset: Dataset,
                      test_index: int, verbose: bool = False):
        message = []
        isGpt = 'gpt' in self.model_uri
        isGemini = 'gemini' in self.model_uri
        if isGpt:
            message.append({'role': 'developer', 'content': f'{prompt_template.definition} {prompt_template.instruction}'})

        for index in train_indexes:
            input_example = prompt_template.create_example(self.project_properties(train_dataset, index))
            input_answer = prompt_template.create_answer(self.project_properties(train_dataset, index))

            if isGpt:
                message.append({'role': 'user', 'content': input_example})
                message.append({'role': 'assistant', 'content': input_answer})
            elif isGemini:
                message.append(f'<EXAMPLE>\n{input_example}{input_answer}\n</EXAMPLE>')
            else:
                message.append(f'{input_example}{input_answer}')


        test_properties = self.project_properties(test_dataset, test_index)
        if 'label' in test_properties:
            test_properties['label'] = ''
        input_question = prompt_template.create_example(test_properties)
        if isGpt:
            message.append({'role': 'user', 'content': input_question})
        else:
            message.append(f'{input_question}')

        if isGpt:
            prompt = message
        else:
            prompt = f'{prompt_template.definition} {prompt_template.instruction}\n{"".join(message)}'
        if verbose:
            print(f'Prompt:\n {prompt}')
        return prompt