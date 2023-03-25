import csv
from re import I

WORD_LEN = 5

def foldl(func, init, seq):
    if not seq:
        return init
    else:
        return foldl(func, func(init, seq[0]), seq[1:])

def main(index_to_words_dicts, answers_set):
    # list of WORD_LEN dictionaries mapping letters to a list of words 
    # w/ the key letter at this index
    populate_index_to_words_dicts(index_to_words_dicts, answers_set)
    user_input = input("guess details> ").lower().split()
    while user_input != "found":
        locked_dict, loose_dict, continue_guessing_flag = parse_input(user_input)
        if continue_guessing_flag:
            guess_set = find_guesses(locked_dict, loose_dict, index_to_words_dicts, answers_set)
            print("possible guesses: " + str(guess_set))
        user_input = input("guess details > ").lower().split()


def populate_index_to_words_dicts(index_to_word_list_dicts, answers_set):
    with open('valid_words.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            for word in row:    # figure out a better way of stripping them later
                answers_set.add(word)
                index = 0
                for letter in word:
                    if letter in index_to_word_list_dicts[index].keys(): 
                        index_to_word_list_dicts[index][letter].add(word) # letter has already been added to this dict
                    else:
                        index_to_word_list_dicts[index][letter] = {word} # add letter to dict for first time
                    index+=1

def parse_input(user_input):
    locked_dict = {} 
    loose_dict = {}
    remaining_indices = range(WORD_LEN)
    exit = ({}, {}, False)
    for i in range(len(user_input)):
        arg = user_input[i] 
        if arg == "found":
            print("Congrats!")
            return exit
        # begin locked / green args
        elif arg == "-g":
            status = "locked"
        # begin loose / yellow args
        elif arg == "-y":
            status = "loose"
        # check that a flag was passed
        if status == "locked" or status == "loose":
            dict_to_fill = eval(status + "_dict")
            i = parse_guess_details(dict_to_fill, user_input, i, remaining_indices, status)
            if (i < 0): 
                return exit
        else:
            print("Incorrect usage. Correct usage: -g <letter> <position> -y <letter> <position> <position>")
            return exit 
    return locked_dict, loose_dict, True

def parse_guess_details(to_fill_dict, user_input, prev_index, loose_indices, status):
    locked_letter = "0"
    exit = -1
    for i in range(prev_index + 1, len(user_input)):
        arg = user_input[i]
        if arg.isalpha() and locked_letter not in to_fill_dict.keys():
            print("Missing indices for a " + status + " letter '" + locked_letter + "'")
            return exit
        elif arg.isalpha():
            locked_letter = arg 
        elif not arg.isalpha() and locked_letter != "0":
            try:
                index_of_letter = int(user_input[i]) - 1
            except: 
                print("Index was not an integer or improperly entered.")
                return exit
            if index_of_letter < 0:
                print("Input position of letter must be between 1 and " + str(WORD_LEN) + ".")
                return exit
            if locked_letter not in to_fill_dict.keys(): # todo: way to speed this up?
                to_fill_dict[locked_letter] = [index_of_letter]
            else:
                to_fill_dict[locked_letter] = to_fill_dict[locked_letter].append(index_of_letter)
            loose_indices.remove(index_of_letter)
        elif arg == "-y" or arg == "-g":
            return i - 1
        else:
            print("Unknown error in parsing locked arguments.")
            return exit
    print("dbg: returning i = " + str(i) + " from parse_locked")
    return i # possbug: need to return len(user_input) - 1 ?


def find_guesses(locked_dict, loose_dict, index_to_words_dicts, answers_set):
    # populate suggested set of locked letters
    locked_list = list_from_locked_letters(locked_dict, index_to_words_dicts)
    if len(locked_list) > 0:
        locked_set = foldl(lambda x, y: x.intersection(y), locked_list[0], locked_list)
    else: 
        locked_set = answers_set

    loose_list = list_from_loose_letters(loose_dict, index_to_words_dicts)
    if len(loose_list) > 0:
        loose_set = foldl(lambda x, y: x.intersection(y), loose_list[0], loose_list)
    else: #letter_set is empty
        loose_set = answers_set

    # check intersection between locked and loose suggestions -> viable answers
    suggestions = locked_set.intersection(loose_set)
    return suggestions    

def list_from_locked_letters(locked_dict, letter_to_words_dicts):
    index_to_words_sets = [set() for i in range(WORD_LEN)]
    locked_list = []
    for letter_to_indices in locked_dict.items():
        letter = letter_to_indices[0]
        indices = letter_to_indices[1]
        locked_list.append(set())
        for index, i in enumerate(indices):
            # todo: FIX PER INDEX / DUPLICATE FUNCTIONALITY
            dict_at_index = letter_to_words_dicts[index]
            index_to_words_sets[index] = dict_at_index[letter]
    locked_indices = list(locked_dict.values())
    locked_list = [index_to_words_sets[i] for i in locked_indices]
    return locked_list

def list_from_loose_letters(loose_dict, index_to_words_dicts):
    # populate suggested set of loose letters
    loose_list = []
    # loose : dict{letters -> [indices]}
    for letter_to_indices in loose_dict.items():
        letter : str = letter_to_indices[0]
        indices : list[int] = letter_to_indices[1]
        loose_list.append(set())
        for index, i in enumerate(indices):
            try:
                dict_at_index = index_to_words_dicts[index]
                loose_list[i] = loose_list[i].union(dict_at_index[letter])
            except:
                print("dictionary skipped at letter " + str(letter) + ", index " + str(index))
    return loose_list


if __name__ == "__main__":
    index_dicts = [{} for i in range(WORD_LEN)] 
    empty_answer_set = set()
    main(index_dicts, empty_answer_set)