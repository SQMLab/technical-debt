from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from Model import Model
from PromptTemplate import PromptTemplate
from util import *


class HuggingFaceModel(Model):
    def __init__(self, task_type: str, model_uri: str, known_labels: set[str], unmatched_label: str):
        super().__init__(task_type, model_uri, known_labels, unmatched_label)
        self.tokenizer = AutoTokenizer.from_pretrained(model_uri)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_uri, device_map="auto")
        self.train_dataset = None
        self.train_indexes = None

    def fit(self, dataset: Dataset):
        self.train_dataset = dataset

    def predict(self, dataset: Dataset,  dataset_name: str, prompt_template: PromptTemplate, train_strategy: TrainStrategy,
                n_shot_size: int,
                verbose: bool = False):
        super().predict_start(dataset)
        label_predictions = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, n_shot_size, train_strategy)
            prompt = self.create_prompt(prompt_template, self.train_dataset, train_indexes, dataset, index)
            tokens = self.tokenizer(prompt, return_tensors="pt")
            tokens['input_ids'] = tokens.input_ids.to(self.model.device)
            input_ids = tokens.input_ids
            # print(len(input_ids[0]))
            # detokenized_text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
            # print(detokenized_text)
            output = self.model.generate(input_ids)
            # print(self.tokenizer.decode(outputs[0], skip_special_tokens=False))
            label_predictions.append(
                self.format_label(self.tokenizer.decode(output[0], skip_special_tokens=True), verbose))
        return super().predict_end(dataset, dataset_name, label_predictions, f'{n_shot_size}-shot')
