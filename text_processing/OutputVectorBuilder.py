from abc import abstractmethod, ABCMeta

from data_module.models import ProcessedDescription
from text_processing import NGramUtils


class OutputVectorBuilder(metaclass=ABCMeta):
    def __init__(self):
        self.vector_map = dict()
        self._init_vectors()

    def get_vector(self, examination_id, eye):
        if (examination_id, eye) in self.vector_map:
            return self.vector_map[(examination_id, eye)]
        else:
            return [0 for _ in range(0, self._vector_size())]

    def _init_vectors(self):
        descriptions = ProcessedDescription.objects.exclude(examination_id__isnull=True)
        for desc in descriptions:
            self.vector_map[(desc.examination_id, desc.eye)] = self._build_vector(desc.text)

    @abstractmethod
    def _build_vector(self, text):
        raise NotImplementedError

    @abstractmethod
    def _vector_size(self):
        raise NotImplementedError

    def _create_vector(self, text, phrases):
        return [int(NGramUtils.is_phrase_present(phrase, text)) for phrase in phrases]
