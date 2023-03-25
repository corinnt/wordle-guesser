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
        locked_dict, loose_dict, continue_flag = read_locked_loose(user_input)
        if continue_flag:
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

def read_locked_loose(user_input):
    locked_dict = {} 
    loose_dict = {}
    remaining_indices = range(WORD_LEN)
    #control flags
    lock_loose = -1 #initialize as -1 to be neither locked mode nor loose mode
    prev_is_alpha = False 
    continue_flag = True
    for i in range(len(user_input)):
        arg = user_input[i] 
        if arg == "found":
            print("Congrats!")
            continue_flag = False
        # begin locked / green args
        elif arg == "-g":
            lock_loose = 0
        # begin loose / yellow args
        elif arg == "-y": 
            lock_loose = 1

        elif len(arg) > 1 or lock_loose < 0:
            print("incorrect argument")
            continue_flag = False
        # parsing locked args
        elif lock_loose == 0 and arg.isalpha() and not prev_is_alpha: 
            try:
                arg_as_int = int(user_input[i + 1])
                prev_is_alpha = True
            except: 
                print("index was not an integer")
                continue_flag = False
            if arg in locked_dict.items():
                locked_dict[arg] = locked_dict[arg].append(arg_as_int)
            else:
                locked_dict[arg] = [arg_as_int]
        # lock_loose = 1 -> loose letters to follow
        elif lock_loose == 0 and prev_is_alpha:  
            try:
                remaining_indices.remove(int(arg))
                prev_is_alpha = False
            except:   # 'index' couldn't be removed, was out of range or not a number
                print("'index' was out of range, duplicate, or not a number @" + str(i) + ", " + arg)
                continue_flag = False

        else:
            loose_dict[arg] = remaining_indices # loose dict: maps letter to list of poss indices

    return locked_dict, loose_dict, continue_flag

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

def list_from_locked_letters(locked_dict, index_to_words_dicts):
    index_to_words_sets = [set() for i in range(WORD_LEN)]
    locked_list = []
    for letter_to_indices in locked_dict.items():
        letter = letter_to_indices[0]
        indices = letter_to_indices[1]
        locked_list.append(set())
        for index, i in enumerate(indices):
            # todo: FIX PER INDEX / DUPLICATE FUNCTIONALITY
            dict_at_index = index_to_words_dicts[index]
            index_to_words_sets[index] = dict_at_index[letter]
    locked_indices = list(locked_dict.values())
    locked_list = [index_to_words_sets[i] for i in locked_indices]
    return locked_list

def list_from_loose_letters(loose_dict, index_to_words_dicts):
    # populate suggested set of loose letters
    loose_list = []
    # loose : dict{letters -> [indices]}
    for letter_to_indices in loose_dict.items():
        letter = letter_to_indices[0]
        indices = letter_to_indices[1]
        loose_list.append(set())
        for index, i in enumerate(indices):
            try:
                loose_list[i] = loose_list[i].union(eval("dict_" + str(index))[letter])
            except:
                print("dictionary skipped at letter " + str(letter) + ", index " + str(index))
    return loose_list

if __name__ == "__main__":
    index_dicts = [{} for i in range(WORD_LEN)] 
    empty_answer_set = set()
    main(index_dicts, empty_answer_set)