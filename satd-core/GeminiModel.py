import os

import google.generativeai as genai

from Model import Model
from PromptTemplate import PromptTemplate
from util import *


class GeminiModel(Model):
    def __init__(self, task_type: str, model_uri: str, known_labels: set[str], unmatched_label: str):
        super().__init__(task_type, model_uri, known_labels, unmatched_label)
        self.model = genai.GenerativeModel(model_uri)
        self.train_dataset = None
        self.train_indexes = None
        print(os.getenv("GOOGLE_API_KEY"))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def fit(self, dataset: Dataset):
        self.train_dataset = dataset

    def predict(self, dataset: Dataset, dataset_name: str, prompt_template: PromptTemplate, train_strategy: TrainStrategy, n_shot_size: int, verbose: bool = False):
        super().predict_start(dataset)
        label_predictions = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, n_shot_size, train_strategy)
            prompt = self.create_prompt(prompt_template, self.train_dataset, train_indexes, dataset, index)
            label_predictions.append(self.format_label(predict_with_gemini(self.model, prompt), verbose))
        return super().predict_end(dataset, dataset_name, label_predictions)
