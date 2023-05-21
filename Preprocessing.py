import pandas
import string
import parsivar


# some preparations before starting normalization, tokenization, removing stopwords and stemming
# this function removes end of message, and removes punctuations
def preparation(content):
    # deleting end of message
    content = content.rstrip(string.whitespace + 'انتهای پیام/')
    # removing punctuations
    content = content.translate(content.maketrans("", "", string.punctuation + "؛،،؟_ـ”«»؛"))
    return content


# normalization
def normalizer(content):
    try:
        normalizer = parsivar.Normalizer(statistical_space_correction=True)
        return normalizer.normalize(content)
    except Exception as e:
        print(f"Error in normalization: {e}")
        return None


# tokenization
def tokenizer(content):
    tokenizer = parsivar.Tokenizer()
    tokens = tokenizer.tokenize_words(content)
    dictionary = {}
    for index in range(len(tokens)):
        token = tokens[index]
        if token in dictionary:
            dictionary[token].append(index)
        else:
            dictionary[token] = [index]
    return dictionary


import hazm
# Removing stop words
# in this project I prefer using parsivar but since parsivar doesn't have a
# built-in stop words list for persian language i use hazm which has one
def remove_persian_stop_words(dictionary):
    persian_stop_words = hazm.stopwords_list()
    filtered_dictionary = {}

    for token, index in dictionary.items():
        if token not in persian_stop_words:
            filtered_dictionary[token] = index

    return filtered_dictionary


# stemming
def stemmer(dictionary):
    stemmer = parsivar.FindStems()
    stemmed_dictionary = {}

    for key, value in dictionary.items():
        stem = stemmer.convert_to_stem(key)
        if stem not in stemmed_dictionary:
            stemmed_dictionary[stem] = []
        for i in range(len(value)):
            stemmed_dictionary[stem].append(value[i])

    return stemmed_dictionary


# preprocessor function which performs all the previous functions to
# the input content
def preprocessor(content):
    content = preparation(content)
    content = normalizer(content)
    content = tokenizer(content)
    content = remove_persian_stop_words(content)
    content = stemmer(content)

    return content


# # Reading the original JSON file and creating a copy
# data_frame = pandas.read_json('IR_data_news_12k.json')
# test_data_frame = data_frame.copy()
#
# # Transpose the copy for easier access to content data
# test_data_frame = test_data_frame.transpose()

# # Testing the entire preprocessing algorithm on a single content
# print(test_data_frame['content'].iloc[0])
# print(preprocessor(test_data_frame['content'].iloc[0]))


# # Preprocessing the entire file and saving it to disk
# test_data_frame['content'] = test_data_frame['content'].apply(preprocessor)
# test_data_frame.to_pickle('preprocessed.pickle')



# # Load the pickle file
# data_frame = pandas.read_pickle('preprocessed.pickle')
#
# # Print some contents of the DataFrame
# print(data_frame['content'].iloc[0])
# print(data_frame['content'].iloc[100])
