import itertools
from collections import Counter

from data_module.models import ProcessedDescription


class NGramCounter:
    def get_n_gram_histogram(self, n, omission_threshold=0, limit=None):
        def n_gram_generator(words):
            return set({tuple(words[i:i + n]) for i in range(0, len(words) - n + 1)})

        return self._get_gram_histogram(n_gram_generator, omission_threshold, limit)

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
            return set(self._k_skip_n_gram(words, n, k))

        return self._get_gram_histogram(k_skip_n_gram_generator, omission_threshold, limit)

    def _k_skip_n_gram(self, words, n, k):
        def skip_grams_starting_from(start_index):
            mandatory_element = words[start_index]
            subsequence = words[start_index + 1: start_index + n + k]
            return [(mandatory_element,) + combination for combination in itertools.combinations(subsequence, n - 1)]

        grams = [skip_grams_starting_from(i) for i in range(0, len(words) - n + 1)]
        return list(itertools.chain.from_iterable(grams))
