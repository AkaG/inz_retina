from text_processing.OutputVectorBuilder import OutputVectorBuilder


class NGramVectorBuilder(OutputVectorBuilder):
    def __init__(self, ngrams):
        self.phrases = [' '.join(words) for words in ngrams]
        super().__init__()

    def _build_vector(self, text):
        return self._create_vector(text, self.phrases)

    def _vector_size(self):
        return len(self.phrases)
