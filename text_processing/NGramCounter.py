from collections import Counter

from data_module.models import ProcessedDescription
from text_processing import NGramUtils


class NGramCounter:
    def get_n_gram_histogram(self, n, omission_threshold=0, limit=None):
        def gram_generator(words):
            return NGramUtils.generate_n_grams(words, n)

        return self._get_gram_histogram(gram_generator, omission_threshold, limit)

    def _get_gram_histogram(self, gram_generator, omission_threshold, limit):
        descriptions = ProcessedDescription.objects.all()
        histogram = Counter()
        for desc in descriptions:
            text = desc.text
            if text:
                all_words = text.split(' ')
                n_grams = gram_generator(all_words)
                histogram.update(n_grams)
        return Counter({key: count for key, count in histogram.most_common(limit) if count >= omission_threshold})

    def get_k_skip_n_gram_histogram(self, n, k, omission_threshold=0, limit=None):
        def k_skip_n_gram_generator(words):
            return NGramUtils.generate_k_skip_n_grams(words, n, k)

        return self._get_gram_histogram(k_skip_n_gram_generator, omission_threshold, limit)
