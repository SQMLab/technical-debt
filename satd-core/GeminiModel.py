
import Model, TrainStrategy, PromptTemplate
from util import *
import google.generativeai as genai
import os


class GeminiModel(Model):
    def __init__(self, task_type: str, model_uri: str, known_labels: set[str], unmatched_label: str,
                 prompt_template: PromptTemplate, train_strategy: TrainStrategy, n_shot_size: int,
                 verbose: bool = False):
        super().__init__(task_type, model_uri, known_labels, unmatched_label, verbose)
        self.model = genai.GenerativeModel(model_uri)
        self.prompt_template = prompt_template
        self.train_strategy = train_strategy
        self.n_shot_size = n_shot_size
        self.train_dataset = None
        self.train_indexes = None
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def fit(self, dataset: Dataset):
        self.train_dataset = dataset

    def predict(self, dataset: Dataset):
        super().predict_start(dataset)
        label_predictions = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, self.n_shot_size, self.train_strategy)
            prompt = self.create_prompt(self.prompt_template, self.train_dataset, train_indexes, dataset, index)
            label_predictions.append(self.format_label(predict_with_gemini(self.model, prompt)))
        return super().predict_end(dataset, label_predictions)
