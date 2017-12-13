import itertools


def generate_n_grams(words, n):
    return set({tuple(words[i:i + n]) for i in range(0, len(words) - n + 1)})


def generate_k_skip_n_grams(words, n, k):
    def skip_grams_starting_from(start_index):
        mandatory_element = words[start_index]
        subsequence = words[start_index + 1: start_index + n + k]
        return [(mandatory_element,) + combination for combination in itertools.combinations(subsequence, n - 1)]

    grams = [skip_grams_starting_from(i) for i in range(0, len(words) - n + 1)]
    return set(itertools.chain.from_iterable(grams))


def normalize_string(s):
    return ' %s ' % s


def is_phrase_present(phrase, text):
    return normalize_string(phrase) in normalize_string(text)
