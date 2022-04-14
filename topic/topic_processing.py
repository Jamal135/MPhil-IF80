# Creation Date: 14/04/2022


# Source 1: https://medium.com/analytics-vidhya/topic-modeling-using-gensim-lda-in-python-48eaa2344920
# Source 2: https://www.machinelearningplus.com/nlp/topic-modeling-visualization-how-to-present-results-lda-models/


from nltk.corpus import stopwords
import re
import os
import spacy
import pandas
import gensim
import pyLDAvis
import gensim.corpora
from pprint import pprint
import pyLDAvis.gensim_models
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess
from warnings import filterwarnings
filterwarnings('ignore')


def first_setup():
    import nltk
    nltk.download('stopwords')
    os.system("python3 -m spacy download en_core_web_sm")


def load_data(filename: str, column: str):
    ''' Returns: Loaded data structure of selected CSV column. '''
    df = pandas.read_csv(f"topic/{filename}") 
    df = df.dropna(subset=[column]) # Remove nan values
    return df[column].values.tolist()


def sentence_to_words(sentences):
    for sentence in sentences: # deacc=True removes punctuations
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))


def cleaning(data):
    ''' Returns: Data cleaned and tokenized ready for preprocessing. '''
    data = [re.sub('\s+', ' ', sent) for sent in data] # Remove new lines
    data = [re.sub("\'", "", sent) for sent in data] # Remove single quotes
    return list(sentence_to_words(data)) # Split sentences to words


def remove_stopwords(texts, extra_stopwords: list = []):
    stop_words = stopwords.words('english')
    stop_words.extend(['from', 'subject', 're', 'edu', 'use'] + extra_stopwords)
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]


def make_bigrams(texts, bigram_mod):
    return [bigram_mod[doc] for doc in texts]


def make_trigrams(texts, bigram_mod, trigram_mod):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]


def lemmatization(texts, tags):
    ''' Information: https://spacy.io/api/annotation '''
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append(
            [token.lemma_ for token in doc if token.pos_ in tags])
    return texts_out


def preprocessing(data, stopwords: bool = True, bigrams: bool = True, trigrams: bool = True, 
                    lemmatize: bool = True, tags: list = ['NOUN', 'ADJ', 'VERB', 'ADV'],
                    gram_threshold: int = 100, extra_stopwords: list = []):
    ''' Returns: Data preprocessed as specified ready for LDA analysis. '''
    bigram = gensim.models.Phrases(data, min_count=5, threshold=gram_threshold)
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram = gensim.models.Phrases(bigram[data], threshold=gram_threshold)
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    if stopwords:
        data = remove_stopwords(data, extra_stopwords)
    if bigrams:
        data = make_bigrams(data, bigram_mod)
    if trigrams:
        data = make_trigrams(data, bigram_mod, trigram_mod)
    if lemmatize:
        data = lemmatization(data, tags)
    return data


def LDA_model_fit(lda_model, corpus, data, id2word):
    perplexity = lda_model.log_perplexity(corpus) # Measure model accuracy, lower better
    coherence_model_lda = CoherenceModel(
        model=lda_model, texts=data, dictionary=id2word, coherence='c_v')
    coherence = coherence_model_lda.get_coherence()
    return perplexity, coherence


def visualise(lda_model, corpus, filename):
    ''' Returns: Visualisations of LDA model results. '''
    vis = pyLDAvis.gensim_models.prepare(
        lda_model, corpus, dictionary=lda_model.id2word)
    pyLDAvis.save_html(vis, f'topic/LDAvis_{filename[:-4]}.html')


def LDA_topic_modelling(filename, column, topic_count: int = 10, iterations: int = 10, 
                        chunks: int = 100, stopwords: bool = True, bigrams: bool = True, 
                        trigrams: bool = True, lemmatize: bool = True, 
                        tags: list = ['NOUN', 'ADJ', 'VERB', 'ADV'],
                        gram_threshold: int = 100, extra_stopwords: list = [],
                        visualisations: bool = True):
    ''' Purpose: Develops and visualises LDA topic model of data. '''
    if not filename.endswith('.csv'):
        filename += '.csv'
    data = load_data(filename, column)
    data = cleaning(data)
    data = preprocessing(data, stopwords, bigrams, trigrams, lemmatize, tags,
                         gram_threshold, extra_stopwords)
    id2word = gensim.corpora.Dictionary(data) # Create Dictionary
    texts = data # Create Corpus
    corpus = [id2word.doc2bow(text) for text in texts]
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word,
                                                num_topics=topic_count, random_state=100,
                                                update_every=1, chunksize=chunks,
                                                passes=iterations, alpha='auto',
                                                per_word_topics=True)
    pprint(lda_model.print_topics())
    #doc_lda = lda_model[corpus]
    perplexity, coherence = LDA_model_fit(lda_model, corpus, data, id2word)
    print(f'Perplexity: {perplexity}')
    print(f'Coherence Score: {coherence}')
    if visualisations:
        visualise(lda_model, corpus, filename)


if __name__ == "__main__":
    LDA_topic_modelling("test_data", "Review", bigrams=False, trigrams=False, lemmatize=False, topic_count=20)
