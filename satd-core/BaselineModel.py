import jpype
import jpype.imports
from jpype.types import JArray, JString
import os
from dotenv import load_dotenv
from Model import Model
from datasets import Dataset
import pandas as pd
from OutputLabelConverter import OutputLabelConverter
load_dotenv()
from util import get_default_JVM_path

class BaselineModel(Model):
    def __init__(self, task_type: str, model_uri: str, output_label_converter: OutputLabelConverter, mode, algorithm,
                 data_directory: str):
        super().__init__(task_type, model_uri, output_label_converter, 10000)
        self.data_directory = data_directory
        self.mode = mode
        self.algorithm = algorithm

    def fit(self, dataset: Dataset):
        pass

    def predict(self, dataset: Dataset, dataset_name: str, verbose: bool = False):
        super().predict_start(dataset)
        print(jpype.isJVMStarted())
        if not jpype.isJVMStarted():
            jar_path = os.path.join(os.getenv('JAR_DETECTOR'), 'MAT.jar')
            # Start JVM
            jpype.startJVM(
            get_default_JVM_path(),
            "-ea",  # enable assertions
            f"-Djava.class.path={jar_path}",
            "--add-opens=java.base/java.lang=ALL-UNNAMED")

            # Import Java classes
        from main import Settings
        from main import Main

        Settings.projectNames = JArray(JString)(["train", "test"])

        args = [
            "-p", os.path.join(f'{self.data_directory}/{self.mode}/input', ''),
            "-o", os.path.join(f'{self.data_directory}/{self.mode}/output', ''),
            "-m", self.algorithm,
            "-s", "MTO"
        ]
        Main.main(JArray(JString)(args))
        #jpype.shutdownJVM()

        predicted_label_df = pd.read_csv(os.path.join(f'{self.data_directory}/{self.mode}/output', f'MTO_{self.algorithm}/result--test.txt'), header=None, names=['label'])
        assert len(predicted_label_df) == len(dataset)
        label_predictions = predicted_label_df['label'].map({0: 'no', 1: 'yes'}).tolist()
        raw_label_predictions = predicted_label_df['label'].map({0: '0', 1: '1'}).tolist()
        return super().predict_end(dataset, dataset_name, label_predictions, raw_label_predictions)