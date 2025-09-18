from OutputLabelConverter import OutputLabelConverter
class SatdToYesNoConverter(OutputLabelConverter):
    def __init__(self, output_label_converter: OutputLabelConverter):
        super().__init__(output_label_converter.known_labels, output_label_converter.unmatched_label)
        self.output_label_converter = output_label_converter
        self.mapper = {'satd': 'yes', 'not-satd': 'no'}
    def convert_label(self, label):
        predicted_output_label = self.output_label_converter.convert_label(label)
        if predicted_output_label in self.mapper:
            return self.mapper[predicted_output_label.lower()]
        else:
            raise KeyError(f'{predicted_output_label}')




