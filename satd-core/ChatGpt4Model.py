from PromptTemplate import PromptTemplate
from Model import Model
from util import *
import os

from openai import OpenAI
from OutputLabelConverter import OutputLabelConverter
import json


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


    def submit_batch(self, dataset: Dataset, dataset_name: str, prompt_template: PromptTemplate,
                     train_strategy: TrainStrategy, n_shot_size: int, verbose: bool = False):
        model_name_suffix = f'{n_shot_size}-shot'
        super().predict_start(dataset, model_name_suffix)
        display_job_name = self.get_output_file_name(model_name_suffix).replace('.csv', '')
        batch_items = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, n_shot_size, train_strategy)
            prompt_msg = self.create_prompt(prompt_template, self.train_dataset, train_indexes, dataset, index, verbose)

            if not self.enable_cache or self.read_from_merged_file(model_name_suffix, dataset['text'][index]) is None:
                batch_items.append({
                    "custom_id": str(dataset['id'][index]),
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {"model": self.model_uri, "messages": prompt_msg},
                })
        if len(batch_items) > 0:
            batch_input_file = self.create_batch_input_file_name(model_name_suffix)
            with open(batch_input_file, 'w') as batch_input_file_stream:
                for item in batch_items:
                    batch_input_file_stream.write(json.dumps(item) + "\n")

            uploaded_file = self.client.files.create(
                file=open(batch_input_file, 'rb'),
                purpose="batch"
            )
            file_batch_job = self.client.batches.create(
                input_file_id=uploaded_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={
                    "description": display_job_name
                })

            self.add_into_batch_job(batch_input_file, file_batch_job.id, display_job_name, None)
            print(f"Created batch job: {file_batch_job.id}")
        else:
            print('No item left for request')

