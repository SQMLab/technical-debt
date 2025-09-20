from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from Model import Model
from PromptTemplate import PromptTemplate
from util import *
from OutputLabelConverter import OutputLabelConverter

class HuggingFaceModel(Model):
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter, enable_cache: bool = False):
        super().__init__(task_type, model_uri, output_label_converter, 100, enable_cache)
        self.tokenizer = AutoTokenizer.from_pretrained(model_uri)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_uri, device_map="auto")
        self.train_dataset = None
        self.train_indexes = None

    def fit(self, dataset: Dataset):
        self.train_dataset = dataset

    def predict(self, dataset: Dataset,  dataset_name: str, prompt_template: PromptTemplate, train_strategy: TrainStrategy,
                n_shot_size: int,
                verbose: bool = False):
        model_name_suffix = self.create_model_suffix(prompt_template, n_shot_size)
        super().predict_start(dataset, model_name_suffix)
        ids = []
        label_predictions = []
        raw_label_predictions = []
        for index in range(dataset.num_rows):
            train_indexes = pick_n_shot(self.train_dataset, dataset, index, n_shot_size, train_strategy)
            input_prompt = self.create_input(prompt_template, self.train_dataset, train_indexes, dataset, index, verbose)
            raw_label = self.read_from_merged_file(model_name_suffix,dataset['hash'][index]) if self.enable_cache else None
            if raw_label is None:
                tokens = self.tokenizer(prompt_template.create_full_instruction() + "\n\n" + input_prompt, return_tensors="pt")
                tokens['input_ids'] = tokens.input_ids.to(self.model.device)
                input_ids = tokens.input_ids
                output = self.model.generate(input_ids, max_new_tokens=128)
                raw_label = self.tokenizer.decode(output[0], skip_special_tokens=True)
            predicted_label = self.output_label_converter.convert_label(raw_label)
            ids.append(dataset['id'][index])
            label_predictions.append(predicted_label)
            raw_label_predictions.append(raw_label)
            if self.enable_cache and ((index + 1) % self.cache_update_batch_size  == 0 or index == dataset.num_rows - 1):
                start_index = max(0, index + 1 - self.cache_update_batch_size)
                self.append_into_merged_file(model_name_suffix, dataset, ids[start_index:], label_predictions[start_index:], raw_label_predictions[start_index:])
        return super().predict_end(dataset, dataset_name, label_predictions, raw_label_predictions, self.create_model_suffix(prompt_template, n_shot_size))
