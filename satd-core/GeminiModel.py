import os

import google.generativeai as genai

from Model import Model
from PromptTemplate import PromptTemplate
from util import *
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions
from google.generativeai import types
@retry(
    stop=stop_after_attempt(10),  # Stop after 5 retries
    wait=wait_exponential(multiplier=2, min=60, max=2 * 60),
    retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),  # Retry on rate limit errors
)
def predict_with_gemini(model, system_instruction, prompt):
    generation_config = types.GenerationConfig(
        # system_instruction= system_instruction,
        temperature=0.0
    )
    return model.generate_content(contents=f'{system_instruction} {prompt}', generation_config=generation_config).text.strip().lower()


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
            label_predictions.append(self.format_label(predict_with_gemini(self.model, f'{prompt_template.definition} {prompt_template.instruction}', prompt), verbose))
        return super().predict_end(dataset, dataset_name, label_predictions)
