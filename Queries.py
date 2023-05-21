import re
import Preprocessing
import parsivar
import hazm
import pickle
import pandas
import textwrap


def get_phrases(input_query):
    # Find all substrings between double quotes
    phrases = re.findall('"([^"]+)"', input_query)

    # Remove the quoted substrings from the input string (if any)
    if phrases:
        output_str = re.sub('"([^"]+)"', '', input_query)
    else:
        output_str = input_query

    # Remove extra spaces
    output_str = ' '.join(output_str.split())
    return phrases, output_str


def get_exclamation_words(input_str):
    exclamations_str = ''
    rest_str = ''

    # Find all words in the input string
    words = re.findall(r'\w+|[!"]+', input_str)

    # Iterate over the words and build the two strings
    is_exclamation = False
    for word in words:
        if word == '!':
            is_exclamation = True
        elif is_exclamation:
            exclamations_str += word + ' '
            is_exclamation = False
        else:
            rest_str += word + ' '

    # Remove extra spaces
    exclamations_str = exclamations_str.strip()
    rest_str = rest_str.strip()

    return exclamations_str, rest_str


def preprocessor(content):
    content = Preprocessing.normalizer(content)

    tokenizer = parsivar.Tokenizer()
    content = tokenizer.tokenize_words(content)

    persian_stop_words = hazm.stopwords_list()
    filtered_content = []

    for token in content:
        if token not in persian_stop_words:
            filtered_content.append(token)

    stemmed_content = []
    stemmer = parsivar.FindStems()
    for token in filtered_content:
        stemmed_content.append(stemmer.convert_to_stem(token))

    return stemmed_content


input_query = input("Enter your query: ")

phrases, output_str = get_phrases(input_query)
exclamations_str, rest_str = get_exclamation_words(output_str)

rest = preprocessor(rest_str)

preprocessed_phrases = []
for phrase in phrases:
    phrase = preprocessor(phrase)
    preprocessed_phrases.append(phrase)
phrases = preprocessed_phrases

exclamations = preprocessor(exclamations_str)




with open('PositionalPostingsList.pickle', 'rb') as file:
    positional_postings_list = pickle.load(file)

with open('preprocessed.pickle', 'rb') as file:
    preprocessed = pickle.load(file)

data_frame = pandas.read_json('IR_data_news_12k.json')
test_data_frame = data_frame.copy()
test_data_frame = test_data_frame.transpose()


# searching

def get_single_words_docs(relevant_documents):
    start = True
    for token in rest:
        try:
            token_postings = positional_postings_list[token].get('postings')
        except KeyError:
            print(f"The token '{token}' does not exist in the positional postings list.")
            continue

        if start:
            for posting in token_postings:
                relevant_documents[posting['doc_id']] = 0
                relevant_documents[posting['doc_id']] += posting.get('f')
                start = False
        else:
            temp = {}
            for posting in token_postings:
                if posting['doc_id'] in relevant_documents.keys():
                    temp[posting['doc_id']] = relevant_documents[posting['doc_id']] + posting.get('f')

            relevant_documents = temp

    return relevant_documents


def get_not_words_docs(relevant_documents):
    for token in exclamations:
        try:
            token_postings = positional_postings_list[token].get('postings')
        except KeyError:
            print(f"The token '{token}' does not exist in the positional postings list.")
            continue
        for posting in token_postings:
            if posting['doc_id'] in relevant_documents.keys():
                del relevant_documents[posting['doc_id']]

    return relevant_documents


def get_phrase_docs(relevant_documents, phrase):

    filtered_postings = []
    relevant_indexes = {}
    first = True
    for token in phrase:
        try:
            token_postings = positional_postings_list[token].get('postings')
        except KeyError:
            print(f"The token '{token}' does not exist in the positional postings list.")
            continue

        temp = []
        if first:
            for posting in token_postings:
                if posting['doc_id'] in relevant_documents.keys():
                    temp.append(posting)
                    relevant_indexes[posting['doc_id']] = posting['positions']
            first = False

        else:
            for posting in token_postings:
                for filtered_posting in filtered_postings:
                    if posting['doc_id'] == filtered_posting['doc_id']:
                        new_relevent_indexes = []
                        for index in relevant_indexes[posting['doc_id']]:
                            for i in posting['positions']:
                                if index + 1 == i:
                                    if posting not in temp:
                                        temp.append(posting)
                                    new_relevent_indexes.append(i)
                        relevant_indexes[posting['doc_id']] = new_relevent_indexes
        filtered_postings = temp

    temp = {}
    for filtered_posting in filtered_postings:
         temp[filtered_posting['doc_id']] = relevant_documents[filtered_posting['doc_id']] \
                                    + len(relevant_indexes[filtered_posting['doc_id']])

    relevant_documents = temp
    return relevant_documents


def get_phrases_docs(relevant_documents):
    for phrase in phrases:
        relevant_documents = get_phrase_docs(relevant_documents, phrase)
        if relevant_documents == {}:
            print("no results found!")
            exit(0)
    return relevant_documents

#######################################################


documents = {}

if rest_str:
    documents = get_single_words_docs(documents)
    if documents == {} :
        print("no results found!")
        exit(0)
else:
    for id in range(12202):
         documents[id] = 0

if exclamations_str:
    documents = get_not_words_docs(documents)
    if documents == {}:
        print("no results found!")
        exit(0)

if phrases:
    documents = get_phrases_docs(documents)


sorted_documents = sorted(documents.items(), key=lambda x: x[1], reverse=True)

top_documents = sorted_documents[:5]

for doc_id, value in top_documents:
    print(f'doc_id: {doc_id}   value: {value}')
    title = test_data_frame['title'].iloc[doc_id]
    content = test_data_frame['content'].iloc[doc_id]
    print(f'title: {title}')
    print("content:")
    # Wrap the content string into multiple lines of max width 80 characters
    wrapped_content = textwrap.fill(content, width=80)
    print(wrapped_content)
    print("--------------------------------------------------------------")








