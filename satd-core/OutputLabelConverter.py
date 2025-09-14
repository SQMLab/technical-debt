from abc import ABC, abstractmethod
class OutputLabelConverter(ABC):
    def __init__(self, known_labels: set[str], unmatched_label: str):
        self.known_labels = set([label.lower() for label in known_labels])
        self.unmatched_label = unmatched_label
    @abstractmethod
    def convert_label(self, label):
        pass