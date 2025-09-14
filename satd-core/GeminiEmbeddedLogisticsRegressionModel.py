from GeminiSentenceTransformer import GeminiSentenceTransformer
from Model import Model
from sklearn.linear_model import LogisticRegression
from datasets import Dataset
class GeminiEmbeddedLogisticsRegressionModel(Model):
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter):
        super().__init__(task_type, model_uri, output_label_converter)
        self.transformer = GeminiSentenceTransformer(model_uri, True)
        self.model = LogisticRegression()

    def fit(self, dataset: Dataset):
        self.model.fit(self.transformer.encode(dataset['text']), dataset['label'])

    def predict(self, dataset: Dataset, dataset_name: str, verbose: bool = False):
        super().predict_start(dataset)
        label_predictions = self.model.predict(self.transformer.encode(dataset['text']))
        raw_label_predictions = []
        for index in range(dataset.num_rows):
            raw_label_predictions.append(label_predictions[index])
            label_predictions[index] = self.format_label(label_predictions[index])
        return super().predict_end(dataset, dataset_name, label_predictions, raw_label_predictions)