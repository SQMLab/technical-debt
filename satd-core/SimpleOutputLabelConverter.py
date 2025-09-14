from OutputLabelConverter import OutputLabelConverter
class SimpleOutputLabelConverter(OutputLabelConverter):
    def __init__(self, known_labels: set[str], unmatched_label: str):
        super().__init__(known_labels, unmatched_label)
    def convert_label(self, label):
        if label in self.known_labels:
            return label
        else:
            return self.unmatched_label

