from text_processing.OutputVectorBuilder import OutputVectorBuilder
from text_processing.RulesParser import RulesParser


class SemanticVectorBuilder(OutputVectorBuilder):
    def __init__(self, phrases_file, rules_file):
        self.phrases = self.__read_lines(phrases_file)
        self.rules = self.__read_lines(rules_file)
        self.parser = RulesParser()
        super().__init__()

    def _build_vector(self, text):
        all_phrases = self._create_vector(text, self.phrases)
        computed_phrases = self._run_rules(text)
        all_phrases += [int(is_present) for is_present in computed_phrases.values()]
        return all_phrases

    def _vector_size(self):
        return len(self.phrases) + len(self.rules)

    def _run_rules(self, text):
        phrases = {}
        self.parser.set_text(text)
        for rule in self.rules:
            result = self.parser.parse(rule)
            name = result[0]
            is_present = result[1]
            phrases[name] = int(is_present)
        return phrases

    def __read_lines(self, filename):
        with open(filename, encoding='UTF-8') as file:
            return file.readlines()
