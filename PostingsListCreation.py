import pandas
import pickle


# this function creates the positional postings list.
# it contains the token, number of docs that contain
# this word, total frequency of this word in the whole
# dataset, and postings of that token. the postings of
# a token contain the doc_id, number of repetitions of
# the word in the document and the positions of the
# word in the document
def positional_postings_lists_builder(data_frame):
    positional_postings_list = {}

    for doc_id, row in data_frame.iterrows():

        # tokens of a single document
        tokens = row['content']

        for token, positions in tokens.items():
            if token not in positional_postings_list:
                # df : document frequency, tf: total frequency of the word
                positional_postings_list[token] = {'df': 0, 'tf': 0, 'postings': []}

            positional_postings_list[token]['df'] += 1
            positional_postings_list[token]['tf'] += len(positions)
            positional_postings_list[token]['postings'].append({
                'doc_id': doc_id,
                'f': len(positions),
                'positions': positions
            })

    return positional_postings_list


# reading the preprocessed data
data_frame = pandas.read_pickle('preprocessed.pickle')

positional_postings_list = positional_postings_lists_builder(data_frame)

# saving the positional postings list to disk
with open('PositionalPostingsList.pickle', 'wb') as file:
    pickle.dump(positional_postings_list, file)



# # reading file and viewing some of the results:
# with open('PositionalPostingsList.pickle', 'rb') as file:
#     positional_postings_list = pickle.load(file)
#
# # print(list(positional_postings_list.keys()))
# print(positional_postings_list['آزاردهنده'])
# print(positional_postings_list['لشگرکشی'])
# print(positional_postings_list['قهرمانی'])
