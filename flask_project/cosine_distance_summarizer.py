import spacy
import numpy as np

nlp = spacy.load("en_core_web_lg")

class CosineDistanceSummarizer(object):

    def get_summary(self, text, reduction_percent, vector_type="occurance", ordered=False):
        doc = nlp(text.lower())
        sentences = list(doc.sents)
        num_sentences = int(round(len(sentences)*(1-reduction_percent)))

        matrix = self._create_cosine_similarity_matrix(sentences, vector_type)
        ranking = np.argsort(-np.sum(matrix, axis=0))
        ordered_ranking = sorted(ranking[:num_sentences])

        summary = ""
        for i in range(num_sentences):
            if ordered:
                summary += str(sentences[ordered_ranking[i]]) + " "
            else:
                summary += str(sentences[ranking[i]])
        return summary

    def _create_cosine_similarity_matrix(self, sentences, vector_type):
        numSentences = len(sentences)
        matrix = np.zeros((numSentences, numSentences))
        for i in range(numSentences):
            for j in range(numSentences):
                if i != j: 
                    if vector_type == "occurance":
                        matrix[i][j] = self._cosine_similarity_occurance(sentences[i], sentences[j])
                    else:
                        matrix[i][j] = self._cosine_similarity_word2vec(sentences[i], sentences[j])
        return matrix

    def _cosine_similarity_word2vec(self, sent1, sent2):
        if sent1.has_vector and sent2.has_vector:
            return sent1.similarity(sent2)
    
    def _cosine_similarity_occurance(self, sent1, sent2):
        desiredPOS = ['PROPN', 'VERB', 'NOUN', 'ADJ']
        all_words = []
        for token in sent1:
            if token.text not in all_words:
                all_words.append(token.text)
        for token in sent2:
            if token.text not in all_words:
                all_words.append(token.text)
        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

        for token in sent1:
            if token.pos_ in desiredPOS:
                vector1[all_words.index(token.text)] += 1
    
        for token in sent2:
           if token.pos_ in desiredPOS:
                vector2[all_words.index(token.text)] += 1
    
        return (np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))