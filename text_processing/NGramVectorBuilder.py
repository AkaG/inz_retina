from data_module.models import ProcessedDescription


class NGramVectorBuilder:
    def __init__(self, ngrams):
        self.key_phrases = [' '.join(words) for words in ngrams]
        self.vector_map = dict()
        self._init_vectors()

    def get_vector(self, examination_id, eye):
        if (examination_id, eye) in self.vector_map:
            return self.vector_map[(examination_id, eye)]
        else:
            return [0 for _ in self.key_phrases]

    def _init_vectors(self):
        descriptions = ProcessedDescription.objects.exclude(examination_id__isnull=True)
        for desc in descriptions:
            self.vector_map[(desc.examination_id, desc.eye)] = self._build_vector(desc.text)

    def _build_vector(self, text):
        return [int(phrase in text) for phrase in self.key_phrases]
