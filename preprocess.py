import csv
import pickle
from wordle_solver import WORD_LEN

def main():
    index_dicts = [{} for i in range(WORD_LEN)] 
    answer_set = set()
    populate_letter_to_words_dicts(index_dicts, answer_set)
    pickle_data(index_dicts, answer_set)

def populate_letter_to_words_dicts(letter_to_words_dicts, answers_set):
    """ Populates letter_to_word_dicts, adds all words to answers_set, no return.
    :param letter_to_words_dicts : list[dict{letter -> {words}}] 
    A dictionary mapping a letter to the set of words which have that letter at this index.
    :param answers_set : set{words} 
    Set of all possible wordle answers.
    """
    with open('data/valid_words.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            for word in row:    # figure out a better way of stripping them later
                answers_set.add(word)
                for index, letter in zip(range(len(word)), word):
                    #print("letter: " + str(letter))
                    if letter in letter_to_words_dicts[index].keys(): 
                        letter_to_words_dicts[index][letter].add(word) # letter has already been added to this dict
                    else:
                        letter_to_words_dicts[index][letter] = {word} # add letter to dict for first time

def pickle_data(index_dicts, answer_set):
    """ Takes in preprocessed dictionary and set of all answers.
        Writes pickled files to pickled_dict + pickled_all_words. 
    """
    dict_filepath = "data/pickled_dict"
    answers_filepath = "data/pickled_all_words"

    dict_pickle = open (dict_filepath, "wb")
    pickle.dump(index_dicts, dict_pickle)
    answer_pickle = open (answers_filepath, "wb")
    pickle.dump(answer_set, answer_pickle)

if __name__ == "__main__":
    main()
