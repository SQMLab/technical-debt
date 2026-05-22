"""DebtHunter SATD detector wrapper.

Wraps the patched DebtHunter JAR (with the -csv CLI flag added in
DebtHunter-Tool/src/main/java/parsing/CsvParsing.java) so it plugs into the
same Model interface used by every other RQ2 baseline.

Layout of files under ``data_directory`` (passed at construction time):

    <data_directory>/
        model/                                # only when retrain=True
            binaryClassifier.model
            multiClassifier.model
        train/
            training.arff                     # generated from the fit() dataset
        <dataset_name>/
            input/<dataset_name>_input.csv    # the test set written verbatim
            output/<dataset_name>_input_predictions.csv  # JAR output

Environment variables (set in satd-core/.env):

    JAR_DETECTOR                directory holding baseline jars. The class
                                resolves the DebtHunter jar by scanning this
                                directory for a file whose name matches
                                "debthunter" case-insensitively and ends in
                                ".jar".
    DEBT_HUNTER_PRETRAINED_DIR  absolute path to the JAR repo's preTrainedModels/
                                directory (containing DHbinaryClassifier.model
                                and DHmultiClassifier.model). Used only when
                                retrain=False so we don't depend on the JAR's
                                cwd.
"""

import os
import subprocess
import pandas as pd
from datasets import Dataset
from dotenv import load_dotenv

from Model import Model
from OutputLabelConverter import OutputLabelConverter

load_dotenv()


class DebtHunterSatdDetectorModel(Model):

    def __init__(self,
                 task_type: str,
                 model_uri: str,
                 output_label_converter: OutputLabelConverter,
                 data_directory: str,
                 retrain: bool = False):
        super().__init__(task_type, model_uri, output_label_converter, 10000)
        self.data_directory = data_directory
        self.retrain = retrain
        os.makedirs(self.data_directory, exist_ok=True)
        os.makedirs(self.model_directory, exist_ok=True)

        self.jar_path = self._resolve_debt_hunter_jar(os.getenv('JAR_DETECTOR'))

        # Only required when retrain=False, because in that case we route the
        # JAR through -m1/-m2 pointing at DebtHunter's released pretrained
        # models to avoid the JAR's hard-coded "./preTrainedModels/..." path.
        self.pretrained_dir = os.getenv('DEBT_HUNTER_PRETRAINED_DIR')

    # ----- paths --------------------------------------------------------

    @staticmethod
    def _resolve_debt_hunter_jar(jar_dir):
        """Find the DebtHunter jar inside ``jar_dir`` by case-insensitive name match.

        ``JAR_DETECTOR`` points at a directory of baseline jars (the same one
        used by the SATD detector wrapper). We scan it for any ``*.jar`` whose
        filename contains ``debthunter`` in any case, so renamed versions like
        ``DebtHunter-0.0.1-SNAPSHOT.jar`` or ``DebtHunter-tool.jar`` all match.
        """
        if not jar_dir:
            raise FileNotFoundError(
                'JAR_DETECTOR is not set; cannot locate the DebtHunter jar.'
            )
        if not os.path.isdir(jar_dir):
            raise FileNotFoundError(
                f'JAR_DETECTOR is not a directory: {jar_dir!r}'
            )
        candidates = sorted(
            f for f in os.listdir(jar_dir)
            if f.lower().endswith('.jar') and 'debthunter' in f.lower()
        )
        if not candidates:
            raise FileNotFoundError(
                f'No .jar matching "debthunter" (case-insensitive) found under {jar_dir!r}. '
                f'Make sure the built DebtHunter jar lives there.'
            )
        if len(candidates) > 1:
            print(
                f'Multiple DebtHunter jars in {jar_dir!r}: {candidates}. '
                f'Using {candidates[0]}.'
            )
        return os.path.join(jar_dir, candidates[0])

    @property
    def model_directory(self):
        return os.path.join(self.data_directory, 'model')

    @property
    def retrained_binary_model_path(self):
        return os.path.join(self.model_directory, 'binaryClassifier.model')

    @property
    def retrained_multi_model_path(self):
        return os.path.join(self.model_directory, 'multiClassifier.model')

    @property
    def pretrained_binary_model_path(self):
        if not self.pretrained_dir:
            return None
        return os.path.join(self.pretrained_dir, 'DHbinaryClassifier.model')

    @property
    def pretrained_multi_model_path(self):
        if not self.pretrained_dir:
            return None
        return os.path.join(self.pretrained_dir, 'DHmultiClassifier.model')

    def _dataset_directory(self, dataset_name: str):
        base = os.path.join(self.data_directory, dataset_name)
        input_dir = os.path.join(base, 'input')
        output_dir = os.path.join(base, 'output')
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        return input_dir, output_dir

    # ----- training -----------------------------------------------------

    @staticmethod
    def _arff_escape(s):
        s = str(s)
        # ARFF quoting: backslash-escape backslashes and single quotes; flatten
        # newlines so each record stays on one line.
        return (
            s.replace("\\", "\\\\")
             .replace("'", "\\'")
             .replace("\n", " ")
             .replace("\r", " ")
        )

    def _write_training_arff(self, dataset: Dataset, arff_path: str):
        df = dataset.to_pandas()
        if 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError('fit() dataset must contain "text" and "label" columns')

        # If the dataset carries DebtHunter-style multi-class labels (e.g. a
        # 'category' column with values like IMPLEMENTATION/DESIGN/...), use
        # them so the multi-class classifier sees the real distribution.
        # Otherwise fall back to a binary collapse: yes -> IMPLEMENTATION as a
        # placeholder SATD category, no -> WITHOUT_CLASSIFICATION. DebtHunter's
        # internal binarization step will still recover the binary objective
        # for the binary classifier.
        if 'category' in df.columns and df['category'].notna().any():
            categories = df['category'].fillna('WITHOUT_CLASSIFICATION').astype(str)
        else:
            categories = df['label'].astype(str).str.lower().map(
                {'yes': 'IMPLEMENTATION', 'no': 'WITHOUT_CLASSIFICATION'}
            )
            if categories.isna().any():
                bad = df.loc[categories.isna(), 'label'].unique()
                raise ValueError(f'fit() saw unexpected label values: {bad}')

        valid_categories = {
            'TEST', 'IMPLEMENTATION', 'WITHOUT_CLASSIFICATION',
            'DESIGN', 'DEFECT', 'DOCUMENTATION'
        }
        bad = set(categories.unique()) - valid_categories
        if bad:
            raise ValueError(f'training categories outside DebtHunter schema: {bad}')

        os.makedirs(os.path.dirname(arff_path), exist_ok=True)
        with open(arff_path, 'w', encoding='utf-8') as f:
            f.write('@relation comments\n\n')
            f.write('@attribute comment string\n')
            f.write('@attribute classification {'
                    'TEST,IMPLEMENTATION,WITHOUT_CLASSIFICATION,'
                    'DESIGN,DEFECT,DOCUMENTATION}\n\n')
            f.write('@data\n')
            for text, cat in zip(df['text'], categories):
                f.write(f"'{self._arff_escape(text)}',{cat}\n")

    def fit(self, dataset: Dataset):
        """No-op in pretrained mode; trains DebtHunter on ``dataset`` in retrained mode.

        On success the binary and multi-class .model files land at
        ``data_directory/model/{binaryClassifier,multiClassifier}.model``.
        """
        if not self.retrain:
            return

        train_dir = os.path.join(self.data_directory, 'train')
        os.makedirs(train_dir, exist_ok=True)
        arff_path = os.path.join(train_dir, 'training.arff')
        self._write_training_arff(dataset, arff_path)

        cmd = [
            'java', '-jar', self.jar_path,
            '-u', 'second',
            '-l', arff_path,
            '-o', self.model_directory,
        ]
        print('Running:', ' '.join(cmd))
        subprocess.run(cmd, check=True)

        for required in (self.retrained_binary_model_path,
                         self.retrained_multi_model_path):
            if not os.path.exists(required):
                raise FileNotFoundError(
                    f'DebtHunter training finished but expected model missing: {required}'
                )

    # ----- prediction ---------------------------------------------------

    def predict(self, dataset: Dataset, dataset_name: str, verbose: bool = False):
        super().predict_start(dataset)
        input_dir, output_dir = self._dataset_directory(dataset_name)
        input_csv = os.path.join(input_dir, f'{dataset_name}_input.csv')

        df = dataset.to_pandas()
        if 'text' not in df.columns:
            raise ValueError('predict() dataset must contain a "text" column')
        df.to_csv(input_csv, index=False)

        cmd = [
            'java', '-jar', self.jar_path,
            '-u', 'first',
            '-csv', input_csv,
            '-o', output_dir,
        ]

        if self.retrain:
            if not (os.path.exists(self.retrained_binary_model_path)
                    and os.path.exists(self.retrained_multi_model_path)):
                raise FileNotFoundError(
                    f'retrain=True but no retrained models in {self.model_directory}. '
                    'Did you call fit() first?'
                )
            cmd += [
                '-m1', self.retrained_binary_model_path,
                '-m2', self.retrained_multi_model_path,
            ]
        else:
            # Route through -m1/-m2 to avoid the JAR's hard-coded relative path
            # to "./preTrainedModels/...".
            if (self.pretrained_binary_model_path
                    and self.pretrained_multi_model_path
                    and os.path.exists(self.pretrained_binary_model_path)
                    and os.path.exists(self.pretrained_multi_model_path)):
                cmd += [
                    '-m1', self.pretrained_binary_model_path,
                    '-m2', self.pretrained_multi_model_path,
                ]
            else:
                # Fall back to the JAR's hard-coded lookup. Caller must run
                # with DebtHunter-Tool/ as cwd in that case.
                pass

        if verbose:
            print('Running:', ' '.join(cmd))
        subprocess.run(cmd, check=True)

        base = os.path.splitext(os.path.basename(input_csv))[0]
        pred_csv = os.path.join(output_dir, f'{base}_predictions.csv')
        if not os.path.exists(pred_csv):
            raise FileNotFoundError(f'expected prediction file missing: {pred_csv}')

        pred_df = pd.read_csv(pred_csv)

        # DebtHunter preserves row order, but joining by id when available is
        # defensive against any silent reordering.
        if 'id' in pred_df.columns and 'id' in df.columns:
            pred_df = (
                pred_df.set_index('id')
                       .loc[df['id'].tolist()]
                       .reset_index()
            )

        label_predictions = [self.format_label(str(x)) for x in pred_df['label_pred']]
        raw_label_predictions = [str(x) for x in pred_df['label_pred_raw']]

        return super().predict_end(
            dataset, dataset_name, label_predictions, raw_label_predictions
        )
