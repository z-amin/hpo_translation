from enum import Enum

from evaluate import load
from sentence_transformers import SentenceTransformer, util
from torchmetrics.text import TranslationEditRate

# Download the model before the first run
# nltk.download('punkt')
similarity_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
sacrebleu = load("sacrebleu")
ter = TranslationEditRate(return_sentence_level_score=True)


class SimilarityMetric(Enum):
    """Enum for similarity metrics between two sentences.
    Each metric must implement the evaluate method."""
    SIMPLE = 0
    SACREBLEU = 1
    TER = 2
    SEMANTIC_SIMILARITY = 3

    def evaluate(self, reference: str, candidate: str) -> float:
        """Evaluate the given string similarity metric between two strings.
        Performs simple string cleaning for whitespace and punctuation.
        :param reference: reference and official term
        :param candidate: model-produced translated term
        :return: similarity score when evaluating this specific metric
        """
        match self:
            case SimilarityMetric.SIMPLE:
                return 1 if reference == candidate else 0

            case SimilarityMetric.SACREBLEU:
                references = [[reference]]
                predictions = [candidate]
                results = sacrebleu.compute(predictions=predictions,
                                            references=references,
                                            use_effective_order=True)
                return round(results["score"], 1)

            case SimilarityMetric.TER:
                score = ter(reference, candidate)[0].item()
                return round(score, 1)

            case SimilarityMetric.SEMANTIC_SIMILARITY:
                query_embedding = similarity_model.encode(reference)
                passage_embedding = similarity_model.encode(candidate)
                score = util.cos_sim(query_embedding, passage_embedding)[0].item()
                return round(score * 100, 1)

    def __str__(self):
        match self:
            case SimilarityMetric.SIMPLE:
                return "simple"
            case SimilarityMetric.SACREBLEU:
                return "sacrebleu"
            case SimilarityMetric.TER:
                return "'ter'"
            case SimilarityMetric.SEMANTIC_SIMILARITY:
                return "semsim"


if __name__ == "__main__":
    reference = "Le harán la prueba para el Zika durante el embarazo."
    prediction = "Se le hará una prueba para detectar el virus del Zika durante el embarazo."
    for metric in SimilarityMetric:
        print(f"{metric}: {metric.evaluate(reference, prediction)}")
