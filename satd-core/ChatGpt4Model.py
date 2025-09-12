from PromptTemplate import PromptTemplate
from Model import Model
from TrainStrategy import TrainStrategy
from util import *
import google.generativeai as genai
import os

from openai import OpenAI



class ChatGpt4Model(Model):
    def __init__(self, task_type: str, model_uri: str, known_labels: set[str], unmatched_label: str):
        super().__init__(task_type, model_uri, known_labels, unmatched_label)
        self.client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))
        self.train_dataset = None
        self.train_indexes = None
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def fit(self, dataset: Dataset):
        self.train_dataset = dataset

    def predict(self, dataset: Dataset, dataset_name: str, prompt_template: PromptTemplate, train_strategy: TrainStrategy, n_shot_size: int, verbose: bool = False):
        super().predict_start(dataset)
        label_predictions = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, n_shot_size, train_strategy)
            prompt = self.create_prompt(prompt_template, self.train_dataset, train_indexes, dataset, index, verbose=verbose)
            completion = self.client.chat.completions.create(
                model=self.model_uri,
                store=True,
                messages=prompt)
            label_pred = completion.choices[0].message.content.strip().split()[-1].lower()
            label_predictions.append(self.format_label(label_pred))
        return super().predict_end(dataset, dataset_name, label_predictions)
