from typing import Tuple

from pymystem3 import Mystem

mystem = Mystem()


class SentenceAnalyzer:

    def __init__(self, text: str):
        self.word_analyses = mystem.analyze(text)

    def __iter__(self) -> Tuple[str, str]:
        for word_analysis in self.word_analyses:
            if text := word_analysis.get('text'):
                if analysis := word_analysis.get('analysis'):
                    if len(analysis) != 0:
                        if grammar := analysis[0].get('gr'):
                            pos = grammar.split(',')[0].strip('=')
                            yield text, pos
