import pickle
import textwrap
from collections import Counter
from enum import Enum
from Preprocessing import preprocessor
import numpy
import pandas
import math


######### Creating Dictionary ####################################
def get_log_frequency_weight(term_frequency):
    return 1 + math.log10(term_frequency) if term_frequency > 0 else 0

def make_dictionary(data_frame):
    dictionary = {}
    weights = {}

    for doc_id, content in enumerate(data_frame['content']):
        word_frequencies = {word: len(content[word]) for word in content}

        total_doc_weight_squared = 0

        for word, word_frequency in word_frequencies.items():
            weight = get_log_frequency_weight(word_frequency)
            total_doc_weight_squared += weight ** 2

            if word in dictionary:
                dictionary[word][0] += 1
                dictionary[word][1][doc_id] = weight
            else:
                dictionary[word] = [1, {doc_id: weight}]

        weights[doc_id] = numpy.sqrt(total_doc_weight_squared)

    return dictionary, weights


data_frame = pandas.read_pickle('preprocessed.pickle')
# dictionary, lengths = make_dictionary(data_frame)
#
#
# with open('dictionary.pickle', 'wb') as file:
#     pickle.dump(dictionary, file, pickle.HIGHEST_PROTOCOL)
#
# with open('lengths.pickle', 'wb') as file:
#     pickle.dump(lengths, file, pickle.HIGHEST_PROTOCOL)

########################################################################################
########## Answering Queries ###########################################################

with open('dictionary.pickle', 'rb') as file:
    dictionary = pickle.load(file)

with open('lengths.pickle', 'rb') as file:
    lengths = pickle.load(file)


def create_champion_list(dictionary, number_of_champions):
    champion_list = {}
    for term, (total_count, term_frequency) in dictionary.items():
        top_frequency = dict(Counter(term_frequency).most_common(number_of_champions))
        champion_list[term] = [total_count, top_frequency]

    return champion_list if champion_list else {"No champions found."}


def preprocess_query(query):
    content = preprocessor(query)
    word_frequencies = {word: len(content[word]) for word in content}

    for word, word_frequency in word_frequencies.items():
        word_frequencies[word] += get_log_frequency_weight(word_frequency)

    return word_frequencies


class Similarity(Enum):
    JACCARD = 1
    COSINE = 2


def get_cosine_score(preprocessed_query, dictionary):
    similarities = {}
    query_terms = set(preprocessed_query.keys())
    for query_term in query_terms:
        if query_term not in dictionary:
            continue

        idf = math.log10(N / dictionary[query_term][0])
        for doc_id, weighted_term_frequency in dictionary[query_term][1].items():
            similarities[doc_id] = similarities.get(doc_id, 0) \
                                   + weighted_term_frequency * preprocessed_query[query_term] * idf

    for doc_id, similarity in similarities.items():
        similarities[doc_id] = similarity / lengths[doc_id]

    return similarities


def get_jaccard_score(preprocessed_query, dictionary):
    similarities = {}
    query_terms = set(preprocessed_query.keys())
    for query_term in query_terms:
        if query_term not in dictionary:
            continue

        for doc_id, term_frequency in dictionary[query_term][1].items():
            doc_terms = set(data_frame['content'].iloc[doc_id].keys())
            intersection = set.intersection(query_terms, doc_terms)
            union = set.union(query_terms, doc_terms)
            jaccard = len(intersection) / len(union)
            similarities[doc_id] = similarities.get(doc_id, 0) + (jaccard * term_frequency)

    return similarities


def get_score(mode: Similarity, preprocessed_query, dictionary):
    if mode == Similarity.JACCARD:
        return get_jaccard_score(preprocessed_query, dictionary)
    elif mode == Similarity.COSINE:
        return get_cosine_score(preprocessed_query, dictionary)


def get_top_documents(query, champion_list_enable=False):
    preprocessed_query = preprocess_query(query)
    best_results = {}

    if champion_list_enable:
        best_results.update(get_score(similarity, preprocessed_query, champion_list))

    if len(best_results) < K:
        best_results.update(get_score(similarity, preprocessed_query, dictionary))

    top_documents = []
    sorted_scores = sorted(best_results.items(), key=lambda x: x[1], reverse=True)
    for i in range(min(K, len(best_results))):
        top_documents.append(sorted_scores[i])
    return top_documents


def print_results(results):
    if len(results) >= 0:
        for result in results:
            doc_id = result[0]
            url = original_data_frame["url"].iloc[doc_id]
            content = original_data_frame['content'].iloc[doc_id]
            title = original_data_frame['title'].iloc[doc_id]
            print(f"Document ID: {doc_id}")
            print(f"URL: {url}")
            print(f"Title: {title}")
            # print(f"Content:")
            # # Wrap the content string into multiple lines of max width 80 characters
            # wrapped_content = textwrap.fill(content, width=80)
            # print(wrapped_content)
            # print("------------------------------------------------------------------")
    else:
        print("No Results")


original_data_frame = pandas.read_json('IR_data_news_12k.json')
original_data_frame = original_data_frame.transpose()


champion_list = create_champion_list(dictionary, 10)
N = len(original_data_frame)
K = 5

similarity = Similarity.COSINE
query = "ایران"
query = query + '.'
results = get_top_documents(query)
print_results(results)