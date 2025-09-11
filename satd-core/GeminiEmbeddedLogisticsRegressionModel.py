from GeminiSentenceTransformer import GeminiSentenceTransformer
from Model import Model
from sklearn.linear_model import LogisticRegression
from datasets import Dataset
class GeminiEmbeddedLogisticsRegressionModel(Model):
    def __init__(self, task_type: str, model_uri: str, known_labels: set[str], unmatched_label: str):
        super().__init__(task_type, model_uri, known_labels, unmatched_label)
        self.transformer = GeminiSentenceTransformer(model_uri, True)
        self.model = LogisticRegression()

    def fit(self, dataset: Dataset):
        self.model.fit(self.transformer.encode(dataset['text']), dataset['label'])

    def predict(self, dataset: Dataset, verbose: bool = False):
        super().predict_start(dataset)
        label_predictions = self.model.predict(self.transformer.encode(dataset['text']))
        for index in range(dataset.num_rows):
            label_predictions[index] = self.format_label(label_predictions[index])
        return super().predict_end(dataset, label_predictions)