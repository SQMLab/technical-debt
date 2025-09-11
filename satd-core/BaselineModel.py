import jpype
import jpype.imports
from jpype.types import JArray, JString
import os
from dotenv import load_dotenv
from Model import Model
from datasets import Dataset
import pandas as pd
load_dotenv()
BASE_MAT_DIRECTORY = os.getenv('BASE_MAT_DIRECTORY')

class BaselineModel(Model):
    def __init__(self, task_type: str, model_uri: str, known_labels: set[str], unmatched_label: str):
        super().__init__(task_type, model_uri, known_labels, unmatched_label)

    def fit(self, dataset: Dataset):
        pass

    def predict(self, dataset: Dataset, dataset_name: str, verbose: bool = False):
        super().predict_start(dataset)
        print(jpype.isJVMStarted())
        if not jpype.isJVMStarted():
            jar_path = os.path.join(os.getenv('JAR_DETECTOR'), 'MAT.jar')
            # Start JVM
            jpype.startJVM(
            jpype.getDefaultJVMPath(),
            "-ea",  # enable assertions
            f"-Djava.class.path={jar_path}",
            "--add-opens=java.base/java.lang=ALL-UNNAMED")

            # Import Java classes
        from main import Settings
        from main import Main

        Settings.projectNames = JArray(JString)(["train", "test"])

        mode,*_, algorithm = self.model_uri.split('-')
        args = [
            "-p", os.path.join(f'{BASE_MAT_DIRECTORY}/{mode}/input', ''),
            "-o", os.path.join(f'{BASE_MAT_DIRECTORY}/{mode}/output', ''),
            "-m", algorithm,
            "-s", "MTO"
        ]
        Main.main(JArray(JString)(args))
        #jpype.shutdownJVM()

        predicted_label_df = pd.read_csv(os.path.join(f'{BASE_MAT_DIRECTORY}/{mode}/output', f'MTO_{algorithm}/result--test.txt'), header=None, names=['label'])
        assert len(predicted_label_df) == len(dataset)
        label_predictions = predicted_label_df['label'].map({0: 'no', 1: 'yes'}).tolist()
        return super().predict_end(dataset, dataset_name, label_predictions)