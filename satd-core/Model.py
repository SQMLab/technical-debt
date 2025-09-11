from abc import abstractmethod
from datasets import Dataset
from sklearn.metrics import classification_report
import os
from datetime import datetime
from util import report_mismatch
import PromptTemplate

N_SHOT_PROPERTIES = ['text', 'label', 'code_before', 'code_after', 'cot']


class Model:
    def __init__(self, task_type: str, model_uri: str, known_labels: set[str], unmatched_label: str):
        self.task_type = task_type
        self.model_uri = model_uri
        self.known_labels = set([label.lower() for label in known_labels])
        self.unmatched_label = unmatched_label
        self.unknown_labels = []

    @abstractmethod
    def fit(self, dataset: Dataset):
        pass

    @abstractmethod
    def predict(self, dataset: Dataset):
        pass

    def format_label(self, label, verbose: bool = False):
        if label.lower() in self.known_labels:
            return label.lower()
        else:
            if verbose:
                print(f'Unknown Label: {label}')
            self.unknown_labels.append(label)
            return self.unmatched_label

    def predict_start(self, dataset: Dataset):
        print(f'{self.task_type} with {self.model_uri.split("/")[-1]}')
        self.unknown_labels.clear()

    def predict_end(self, dataset: Dataset, label_predictions):
        file_name = f'{self.task_type}_{self.model_uri.split("/")[-1]}'
        test_output = dataset.to_dict()
        test_output['label_pred'] = label_predictions
        if self.unknown_labels:
            print(f'Unknown Labels:\n{self.unknown_labels}')
        timestamp = datetime.now().strftime("%B %d, %Y, %H:%M:%S")
        file = f'{os.getenv("CACHE_DIRECTORY")}/{timestamp}${file_name}.csv'
        print(file)
        print('Test Result:')
        print(classification_report(dataset['label'], label_predictions, zero_division=0, digits=3))
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
        examples = [prompt_template.create_example(self.project_properties(train_dataset, index)) for index in
                    train_indexes]

        test_properties = self.project_properties(test_dataset, test_index)
        if 'label' in test_properties:
            test_properties['label'] = ''
        examples.append(prompt_template.create_example(test_properties))

        prompt = prompt_template.create_prompt(examples)
        if verbose:
            print(f'Prompt:\n {prompt}')
        return prompt