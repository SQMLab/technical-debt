from Model import Model
import jpype
import jpype.imports
from dotenv import load_dotenv
import os
from datasets import Dataset
from OutputLabelConverter import OutputLabelConverter
from util import get_default_JVM_path
load_dotenv()

BASE_SATD_DETECTOR_DIRECTORY = os.getenv('BASE_SATD_DETECTOR_DIRECTORY')

class TextMiningBasedSatdDetectorModel(Model):
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter, retrain: bool = False):
        super().__init__(task_type, model_uri, output_label_converter)
        self.retrain = retrain

    def fit(self, dataset: Dataset):
        if not jpype.isJVMStarted():
            jar_path = os.getenv('SATD_DETECTOR_JAR')
            dependency_path = os.getenv('SATD_DETECTOR_DEPENDENCY')
            jvm_args = ["-Xss512m"]
            jpype.startJVM(get_default_JVM_path(), classpath=[jar_path, dependency_path], )
        if self.retrain:
            from satd_detector.core.train import Train
            try:
                Train.buildModels(os.path.join(BASE_SATD_DETECTOR_DIRECTORY, 'comments.txt'), os.path.join(BASE_SATD_DETECTOR_DIRECTORY, 'labels.txt'), os.path.join(BASE_SATD_DETECTOR_DIRECTORY, 'projects.txt'), f'{BASE_SATD_DETECTOR_DIRECTORY}/models/')
            except Exception as e:
                print("Error:", e)

    def predict(self, dataset: Dataset, dataset_name: str, verbose: bool = False):
        super().predict_start(dataset)
        label_predictions = []
        raw_label_predictions = []
        from satd_detector.core.utils import SATDDetector
        detector1 =  SATDDetector(f'{BASE_SATD_DETECTOR_DIRECTORY}/models/') if self.retrain else SATDDetector()
        for index in range(dataset.num_rows):
            label_pred = 'yes' if detector1.isSATD(dataset['text'][index]) else 'no'
            raw_label_predictions.append(label_pred)
            label_predictions.append(self.format_label(label_pred))

        return super().predict_end(dataset, dataset_name, label_predictions, raw_label_predictions)

