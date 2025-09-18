from Model import Model
from datasets import Dataset, DatasetDict
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from OutputLabelConverter import OutputLabelConverter

class SentenceEmbeddedLogisticsRegressionModel(Model):
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter):
        super().__init__(task_type, model_uri, output_label_converter, 10000)
        self.transformer = SentenceTransformer(model_uri)
        self.model = LogisticRegression()

    def fit(self, dataset: Dataset):
        self.model.fit(self.transformer.encode(dataset['text']), dataset['label'])

    def predict(self, dataset: Dataset, verbose: bool = False):
        super().predict_start(dataset)
        label_predictions = self.model.predict(self.transformer.encode(dataset['text']))
        raw_label_predictions = []
        for index in range(dataset.num_rows):
            label_predictions[index] = self.format_label(label_predictions[index])
            raw_label_predictions.append(label_predictions[index])
        return super().predict_end(dataset, label_predictions, raw_label_predictions, verbose)
