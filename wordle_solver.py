from re import I
import pickle

WORD_LEN = 5

def foldl(func, init, seq):
    if not seq:
        return init
    else:
        return foldl(func, func(init, seq[0]), seq[1:])

def main():
    # list of WORD_LEN dictionaries mapping letters to a list of words 
    # w/ the key letter at this index
    letter_to_words_dicts, answers_set = unpickle_files()
    user_input = input("guess details> ").lower().split()
    continue_guessing_flag = True
    while continue_guessing_flag:
        locked_dict, loose_dict, continue_guessing_flag = parse_input(user_input)
        if continue_guessing_flag:
            guess_set = generate_guesses(locked_dict, loose_dict, letter_to_words_dicts, answers_set)
            print("possible guesses: " + str(guess_set))
            user_input = input("guess details > ").lower().split()

def unpickle_files():
    """
    """
    dict_pickle = open ("pickled_dict", "rb")
    letter_to_words_dicts = pickle.load(dict_pickle)
    answers_pickle = open("pickled_all_words", "rb")
    answers_set = pickle.load(answers_pickle)
    return letter_to_words_dicts, answers_set

def parse_input(user_input): 
    """ Takes in list of user input args, returns populated locked_dict and loose_dict, continue_flag
    :param user_input : list[str] from user input
    :return locked_dict : dict[letter -> [indices]] - locked in/green letter mapped to the indices at which it occurs
    :return loose_dict : dict[letter -> [indices]] - loose/yellow letter mapped to the indices at which it may occur
    :return continue_flag : Boolean - True when input was properly formatted and which main() should generate guesses
    """
    locked_dict = {} 
    loose_dict = {}
    exit = ({}, {}, False)
    i = 0
    status = ""
    while (i < len(user_input)):
        arg = user_input[i] 
        if arg == "found":
            print("Congrats!")
            i = len(user_input)
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
            i = parse_guess_details(dict_to_fill, user_input, i, status)
            if (i < 0): 
                return exit
        else:
            print("Incorrect usage. Correct usage: -g <letter> <position> -y <letter> <position> <position>")
            return exit 
    return locked_dict, loose_dict, True

def parse_guess_details(to_fill_dict, user_input, prev_index, status):
    """ Takes in locked or loose dictionary to fill, user input, 
        latest index parsed in user_input, "locked" or "loose" status
    """
    letter = "0"
    exit = -1
    if (status == "locked"):
        valid_indices = []
    else: 
        valid_indices = list(range(WORD_LEN))
    letter_valid_indices = []
    for i in range(prev_index + 1, len(user_input)):
        arg = user_input[i]
        if arg == "-y" or arg == "-g":
            to_fill_dict[letter] = letter_valid_indices
            return i
        elif arg.isalpha() and letter == "0": # this isn't the first letter -> record valid valid letters
            letter = arg
            letter_valid_indices = valid_indices.copy()
        elif arg.isalpha() and letter != "0": # any # letter is found, so set up 
            to_fill_dict[letter] = letter_valid_indices
            letter = arg 
            letter_valid_indices = valid_indices.copy()
        elif not arg.isalpha() and letter != "0":
            try:
                index_of_letter = int(user_input[i]) - 1
            except: 
                print("Index was not an integer or improperly entered.")
                return exit
            if index_of_letter < 0:
                print("Input position of letter must be between 1 and " + str(WORD_LEN) + ".")
                return exit
            if status == "locked":
                letter_valid_indices.append(index_of_letter) #input indices are good -> add to valid
            else:
                try:
                    letter_valid_indices.remove(index_of_letter) #input indices are bad -> remove from valid
                except:
                    print("index of letter " + index_of_letter + " not found in letter_valid_indices")
        else:
            print("Error in parsing " + status + " arguments.")
            return exit
    to_fill_dict[letter] = letter_valid_indices
    return len(user_input) # possbug: need to return len(user_input) - 1 ?

def generate_guesses(locked_dict, loose_dict, letter_to_words_dicts, answers_set):
    """ Populate suggested set of words which meet locked and loose specifications
    :param locked_dict : 
    :param loose_dict : 
    :param letter_to_words_dicts : list[dict[letter -> set(words)]]
    :param answers_set : set(words) - all possible words
    :return suggestions : set(words) - set of words which are viable guesses
    """
    locked_list = list_from_locked_letters(locked_dict, letter_to_words_dicts)
    if len(locked_list) > 0:
        locked_set = foldl(lambda x, y: x.intersection(y), locked_list[0], locked_list)
    else: 
        locked_set = answers_set

    loose_list = list_from_loose_letters(loose_dict, letter_to_words_dicts)
    if len(loose_list) > 0:
        loose_set = foldl(lambda x, y: x.union(y), loose_list[0], loose_list)
    else: #letter_set is empty
        loose_set = answers_set

    # check intersection between locked and loose suggestions -> viable answers
    suggestions = locked_set.intersection(loose_set)
    return suggestions    


def list_from_locked_letters(locked_dict, letter_to_words_dicts):
    """ Generates a list of sets of words which have the appropriate letter at their indices for each locked index
    :param locked_dict : dict[letter -> list[indices]]
    :param letter_to_words_dicts : list[dict[letter -> set(words)]]
    :return locked_list : list[set(words)] set for each locked index; each set corresponds to all words st the locked letter is at that index
    """
    locked_list = []
    for letter, indices in locked_dict.items():
        for index in indices:
            try:
                letter_to_words_dict = letter_to_words_dicts[index] 
                locked_list.append(letter_to_words_dict[letter])
            except: 
                print("dictionary skipped at letter " + str(letter) + ", index " + str(index))
    return locked_list

def list_from_loose_letters(loose_dict, letter_to_words_dicts):
    """ Generates list of sets of words which have the key letter at their index 
    :param loose_dict : dict[letter -> list[indices]]
    :param letter_to_words_dicts : list[dict[letter -> set(words)]]
    :return locked_list : list[set(words)] set for each loose index; each set corresponds to all words st  loose letter c at that index
    """
    loose_list = []
    # loose_dict : dict{letters -> [indices]}
    for letter, indices in loose_dict.items():
        for meta_i, index in enumerate(indices):
            loose_list.append(set())
            try:
                letter_to_words_dict = letter_to_words_dicts[index]
                new_set_for_index = loose_list[meta_i].union(letter_to_words_dict[letter])
                loose_list.append(new_set_for_index)
            except:
                print("dictionary skipped at letter " + str(letter) + ", index " + str(index))
    return loose_list


if __name__ == "__main__":
    main()