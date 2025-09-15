from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from Model import Model
from PromptTemplate import PromptTemplate
from util import *
from OutputLabelConverter import OutputLabelConverter

class HuggingFaceModel(Model):
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter, enable_cache: bool = False):
        super().__init__(task_type, model_uri, output_label_converter, enable_cache)
        self.tokenizer = AutoTokenizer.from_pretrained(model_uri)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_uri, device_map="auto")
        self.train_dataset = None
        self.train_indexes = None

    def fit(self, dataset: Dataset):
        self.train_dataset = dataset

    def predict(self, dataset: Dataset,  dataset_name: str, prompt_template: PromptTemplate, train_strategy: TrainStrategy,
                n_shot_size: int,
                verbose: bool = False):
        model_name_suffix = f'{n_shot_size}-shot'
        super().predict_start(dataset, model_name_suffix)
        label_predictions = []
        raw_label_predictions = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, n_shot_size, train_strategy)
            prompt = self.create_prompt(prompt_template, self.train_dataset, train_indexes, dataset, index, verbose)
            raw_label = self.read_from_merged_file(model_name_suffix,dataset['text'][index]) if self.enable_cache else None
            if raw_label is None:
                tokens = self.tokenizer(prompt, return_tensors="pt")
                tokens['input_ids'] = tokens.input_ids.to(self.model.device)
                input_ids = tokens.input_ids
                output = self.model.generate(input_ids)
                raw_label = self.tokenizer.decode(output[0], skip_special_tokens=True)
            predicted_label = self.output_label_converter.convert_label(raw_label)
            label_predictions.append(predicted_label)
            raw_label_predictions.append(raw_label)
            if self.enable_cache:
                self.append_into_merged_file(model_name_suffix, dataset, dataset['id'][index], predicted_label, raw_label)
        return super().predict_end(dataset, dataset_name, label_predictions, raw_label_predictions, f'{n_shot_size}-shot')
