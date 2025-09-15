from PromptTemplate import PromptTemplate
from Model import Model
from util import *
import os

from openai import OpenAI
from OutputLabelConverter import OutputLabelConverter


class ChatGpt4Model(Model):
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter, enable_cache: bool):
        super().__init__(task_type, model_uri, output_label_converter, enable_cache)
        self.client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))
        self.train_dataset = None
        self.train_indexes = None

    def fit(self, dataset: Dataset):
        self.train_dataset = dataset

    def predict(self, dataset: Dataset, dataset_name: str, prompt_template: PromptTemplate, train_strategy: TrainStrategy, n_shot_size: int, verbose: bool = False):
        model_name_suffix = f'{n_shot_size}-shot'
        super().predict_start(dataset, model_name_suffix)
        label_predictions = []
        raw_label_predictions = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, n_shot_size, train_strategy)
            prompt = self.create_prompt(prompt_template, self.train_dataset, train_indexes, dataset, index,verbose=verbose)
            raw_label = self.read_from_merged_file(model_name_suffix, dataset['text'][index]) if self.enable_cache else None
            if raw_label is None:
                completion = self.client.chat.completions.create(
                    model=self.model_uri,
                    store=True,
                    messages=prompt)
                raw_label = completion.choices[0].message.content
            predicted_label = self.output_label_converter.convert_label(raw_label)
            raw_label_predictions.append(raw_label)
            label_predictions.append(predicted_label)
            if self.enable_cache:
                self.append_into_merged_file(model_name_suffix, dataset, dataset['id'][index], predicted_label, raw_label)
        return super().predict_end(dataset, dataset_name, label_predictions, raw_label_predictions, f'{n_shot_size}-shot')
