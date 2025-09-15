import os

import google.genai as genai

from Model import Model
from PromptTemplate import PromptTemplate
from util import *
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from OutputLabelConverter import OutputLabelConverter
# @retry(
#     stop=stop_after_attempt(10),  # Stop after 5 retries
#     wait=wait_exponential(multiplier=2, min=60, max=2 * 60),
#     retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),  # Retry on rate limit errors
# )
def predict_with_gemini(client, model_name, system_instruction, prompt):
    generation_config = genai.types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.0
    )
    return client.models.generate_content(model = model_name,
                                          contents=prompt,
                                          config=generation_config).text


class GeminiModel(Model):
    def __init__(self, task_type: str, model_uri: str,  output_label_converter: OutputLabelConverter, enable_cache: bool):
        super().__init__(task_type, model_uri, output_label_converter, enable_cache)
        self.model =  genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.train_dataset = None
        self.train_indexes = None

    def fit(self, dataset: Dataset):
        self.train_dataset = dataset

    def predict(self, dataset: Dataset, dataset_name: str, prompt_template: PromptTemplate, train_strategy: TrainStrategy, n_shot_size: int, verbose: bool = False):
        model_name_suffix  = f'{n_shot_size}-shot'
        super().predict_start(dataset, model_name_suffix)
        label_predictions = []
        raw_label_predictions = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, n_shot_size, train_strategy)
            prompt = self.create_prompt(prompt_template, self.train_dataset, train_indexes, dataset, index, verbose)
            raw_label = self.read_from_merged_file(model_name_suffix, dataset['text'][index]) if self.enable_cache else None
            if raw_label is None:
                raw_label = predict_with_gemini(self.model, self.model_uri,f'{prompt_template.definition}\n{prompt_template.instruction}', prompt)

            predicted_label = self.output_label_converter.convert_label(raw_label)
            raw_label_predictions.append(raw_label)
            label_predictions.append(predicted_label)
            if self.enable_cache:
                self.append_into_merged_file(model_name_suffix, dataset, dataset['id'][index], predicted_label, raw_label)

        return super().predict_end(dataset, dataset_name, label_predictions, raw_label_predictions, model_name_suffix)
