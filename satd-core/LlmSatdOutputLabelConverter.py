from OutputLabelConverter import OutputLabelConverter
class LlmSatdOutputLabelConverter(OutputLabelConverter):
    def __init__(self, known_labels: set[str], unmatched_label: str):
        super().__init__(known_labels, unmatched_label)
    def convert_label(self, label):
        cleaned_label = label
        for key in [':', '**', '.', ',', 'answer', 'label']:
            cleaned_label = cleaned_label.replace(key, '')
        words = cleaned_label.lower().split()
        for word in reversed(words):
            if word in self.known_labels:
                return word
        return self.unmatched_label
