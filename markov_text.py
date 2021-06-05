import mmap
import random
from pathlib import Path

PUNCT = ("!", ",", ".", ";", "?", ":")

def is_letter(char):
    return (ord(char) >= 65 and ord(char) <= 90) or (ord(char) >= 97 and ord(char) <= 122) or ord(char) == 39

def is_punc(char):
    is_punctuation = False

    for i in PUNCT:
        if char == i:
            is_punctuation = True

    return is_punctuation

def get_next_element(file_map, index, file_size):
    
    word_complete = False
    word = ""
    
    while(word_complete == False and index < file_size):
        char = file_map[index:index + 1].decode("utf-8")
        
        # if character is a letter, add to word
        if is_letter(char):
            # print(char)
            word = word + char
            index = index + 1

        # if character is a hypen
        elif (char == "-"):

            # if there is a dash (double hypen)
            if index < file_size and (file_map[index + 1:index + 2].decode("utf-8") == "-"):
                if len(word) > 0:
                    word_complete = True
                else:
                    word = "--"
                    word_complete = True
                    index = index + 2

            # if the hypen signals a hyphenated word, add character to word
            elif index < file_size and is_letter(file_map[index + 1:index + 2].decode("utf-8")):
                word = word + char
                index = index + 1

            # if hypen does not signal a dash or hyphenated word
            else:
                word = word + char
                word_complete = True
                index = index + 1

        # if character is a punctuation mark
        elif (is_punc(char)):
            if len(word) > 0:
                word_complete = True
            else:
                word = word + char
                word_complete = True
                index = index + 1
        
        # if character is not a punctuation mark or letter     
        else:
            word_complete = True
            index = index + 1

    return word, index
    
def get_words(filename):

    # file processing and mapping
    file_object = open(filename, "r+b")
    file_size = Path(filename).stat().st_size
    file_map = mmap.mmap(file_object.fileno(), 0)

    word_dict = {}              # empty word dict
    index = 0                   # index of file map
    original_element = ""       # original word string    
    
    while (index < file_size):
    
        # get element and index value
        element, index = get_next_element(file_map, index, file_size)
        # print(index)
        if not (element in word_dict):
            word_dict.update({element : {}})
            # print(element)
    
        # block to add the current word to the previous word's dictionary
        if (len(word_dict) > 1):
            
            # is current word in the previous word's dictionary?
            if not (element in word_dict[original_element]):
            
                # if not, add it to the dict, with accumulator value of 1
                word_dict[original_element].update({element : 1})
            else:
            
                # if so, increment the word accumulator
                value = word_dict[original_element][element]
                value = value + 1
                word_dict[original_element][element] = value
                
        # save word for next iteration
        original_element = element
    
    # calculate probabilities of words that appear before a certain word
    for i in word_dict:
    
        # calculate sum of all values of sub words (all words that appear before a specific word)
        total = len(word_dict[i])
        
        # calculate probabilites and store them
        for j in word_dict[i]:
            probability = word_dict[i][j] / total
            word_dict[i][j] = probability
    
    file_object.close()

    return word_dict;

# creates sentences using a markov chain  
def create_sentence(word_dict):
    
    sentence = ""
    word_set = set()
    
    # create a set of keys from the word dictionary
    for key in word_dict.items():
        word_set.add(key[0])
    
    # randomly select a word from the word set (all with equal probabilities)
    word = random.choice(list(word_set))
    sentence = sentence + str(word) + " "
    weights = []
    end = False
    
    while end == False:
        sub_word_list = []
        weights = []
        
        for key in word_dict[word].items():
            sub_word_list.append(key[0])

        # print(word_dict[word])
        # print(*sub_word_list)
        
        # create a weights list to hold weights of associated sub words
        for j in word_dict[word]:
            weights.append(word_dict[word][j])
        
        # print(*weights)
        # print(len(weights), len(sub_word_list))
        
        # choose next word from the distribution

        word = random.choices(sub_word_list, weights, k=1)[0]
                
        # alternate use
        # word = random.choices(list(word_dict[word].items()), weights, k=1)[0][0]

        if word == " ":
            print("space")
            
        if is_punc(word):
            sentence = sentence + word
        elif word != "" and word != " ":
            sentence = sentence + " " + word
            
        if word == ".":
            end = True
        
    return sentence

def main():

    word_dict = get_words("text.txt")
    # for key in word_dict.items():
        # print(key, end = " ")
    
    # print()
    print(create_sentence(word_dict))

main()
