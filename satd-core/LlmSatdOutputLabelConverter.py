from OutputLabelConverter import OutputLabelConverter
class LlmSatdOutputLabelConverter(OutputLabelConverter):
    def __init__(self, known_labels: set[str], unmatched_label: str):
        super().__init__(known_labels, unmatched_label)
    def convert_label(self, label):
        clean_prediction_label = label.lower().strip().replace('-', ' ')
        if 'not satd' in clean_prediction_label:
            return 'no'
        elif 'satd' in clean_prediction_label:
            return 'yes'
        else:
            return 'no'
