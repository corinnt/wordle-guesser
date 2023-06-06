from re import I
import pickle
import argparse

WORD_LEN = 5

def main():
    letter_to_words_dicts, answers_set = unpickle_files("data/pickled_dict", "data/pickled_all_words")
    user_input = input("guess details > ").lower().split()
    args = parseArguments(user_input)
    while not args.found:
        locked_dict = parse_guess_details(args.locked)
        loose_dict = parse_guess_details(args.loose)
        guess_set = generate_guesses(locked_dict, loose_dict, letter_to_words_dicts, answers_set)
        print("possible guesses: " + str(guess_set))
        user_input = input("guess details > ").lower().split()
        args = parseArguments(user_input)

def parseArguments(input):
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--locked", nargs='+', help="")
    parser.add_argument("-y", "--loose",  nargs='+', help="")
    parser.add_argument("-f", "--found",  default=None, help="") 
    args = parser.parse_args(input)
    return args

def unpickle_files(dict_path, answers_path):
    """ Takes in filepaths of pickled list of 5 dictionaries and set of answers.
        Returns the unpickled letter_to_words_dicts and set of all answers.
    """
    dict_pickle = open (dict_path, "rb")
    letter_to_words_dicts = pickle.load(dict_pickle)
    answers_pickle = open(answers_path, "rb")
    answers_set = pickle.load(answers_pickle)
    return letter_to_words_dicts, answers_set

def parse_guess_details(input_list):
    """ Takes in dictionary to populate w/ parsed input, user input, 
        latest index parsed in user_input, "locked" or "loose" status,
        returns next unparsed input index or if error, -1.
    """
    new_dict = {}
    if not input_list: return new_dict
    for char in input_list:
        if not char.isnumeric() and not char.isalpha():
            raise Exception("All arguments must be letters or numbers.")
    
    if len(input_list) < 2:
        raise Exception("Must enter at least one letter and index after flag.")

    i = 0
    while i < len(input_list):
        i = parse_letter(i, input_list, new_dict)

    return new_dict

def parse_letter(i, input_list, new_dict):
    if input_list[i].isalpha():
        letter = input_list[i]
        new_dict[letter] = []
        i += 1
    else:
        raise Exception("First character after flag wasn't a letter")

    arg = input_list[i]
    if not arg.isnumeric():
        raise Exception("First character after letter wasn't a valid index")

    while arg.isnumeric() and i < len(input_list):
        arg = input_list[i]
        new_dict[letter].append(arg)
        i += 1

    return i

def has_locked_duplicates(locked_dict):
        all_indices = set()
        count = 0
        for letter, indices in locked_dict.items():
            count += len(indices)
            mini_set = set(indices)
            all_indices = all_indices.union(mini_set)
        if len(all_indices) != count:
            raise Exception("No repeated indices for green/locked letters")

def foldl(func, init, seq):
    if not seq:
        return init
    else:
        return foldl(func, func(init, seq[0]), seq[1:])

def generate_guesses(locked_dict, loose_dict, letter_to_words_dicts, answers_set):
    """ Populate suggested set of words which meet locked and loose specifications
    :param locked_dict : dict[letter -> list[indices]] - maps locked/green letters to indices those letters occur
    :param loose_dict :  dict[letter -> list[indices]] - maps loose/yellow letters to indices those letters may occur
    :param letter_to_words_dicts : list[dict[letter -> set(words)]] - list of dictionaries 
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
        loose_set = foldl(lambda x, y: x.intersection(y), loose_list[0], loose_list)
    else: loose_set = answers_set
    # check intersection between locked and loose suggestions -> viable answers
    suggestions = locked_set.intersection(loose_set)

    return suggestions    


def list_from_locked_letters(locked_dict, letter_to_words_dicts):
    """ Generates a list of sets of words which have the appropriate letter at their indices for each locked/green index
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
                print("Dictionary skipped at letter " + str(letter) + ", index " + str(index))
    return locked_list

def list_from_loose_letters(loose_dict, letter_to_words_dicts):
    """ Generates list of sets of words which have the key letter at their index 
    :param loose_dict : dict[letter -> list[indices]]
    :param letter_to_words_dicts : list[dict[letter -> set(words)]]
    :return loose_list : list[set(words)] set of words for each loose letter which has the letter at a viable index
    """
    loose_list = []
    for letter, indices in loose_dict.items(): 
        compiled_letter_set = set()
        for index in indices:
            invalid_indices = [i for i in list(range(WORD_LEN)) if i not in indices]
            try:
                compiled_letter_set = compiled_letter_set.union(letter_to_words_dicts[index][letter])
                compiled_letter_set = foldl(lambda base_set, i: \
                                        base_set.difference(letter_to_words_dicts[i][letter]),\
                                        compiled_letter_set, invalid_indices)
            except: "Dictionary skipped, but should be fine."
        loose_list.append(compiled_letter_set)
    return loose_list

if __name__ == "__main__":
    main()