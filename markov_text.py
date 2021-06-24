import mmap
import random
from pathlib import Path

# notes
#
# - issue where last word in text may not have any transitions
# - change 'word' to element or item

PUNCT = ("!", ",", ".", ";", "?", ":")

def is_letter(char):
    
    if len(char) == 0:
        return False
    else:
        return (ord(char) >= 65 and ord(char) <= 90) or (ord(char) >= 97 and ord(char) <= 122) or ord(char) == 39

# This method determines if a character is a punctuation mark from PUNCT
def is_punc(char):
    is_punctuation = False

    for i in PUNCT:
        if char == i:
            is_punctuation = True

    return is_punctuation

# This method returns the next word or punctuation mark from the file.
#   The function reads each character sequentially and determines how to process each
#   character/wrod depending on the value of a preceding or succeeding character
def get_next_element(file_map, index, file_size):
    
    word_complete = False   # This vairable will be True once a whole word is read
    word = ""
    
    # This section loops until a separate, complete word is found or until we reach the end of the file
    while(word_complete == False and index < file_size):

        char = file_map[index:index + 1].decode("utf-8", "ignore")
        
        """ DO WE NEED THIS
        while (char == "") and (index < file_size):
            index = index + 1
            char = file_map[index:index + 1].decode("utf-8", "ignore")
        """
        
        # Determine if character is a letter, then add to word
        if is_letter(char):
            word = word + char
            index = index + 1

        # Determine if character is a hyphen, and if so, then determine if it's part of a hypenated word or a dash
        elif (char == "-"):

            if (index < file_size - 1) and (file_map[index + 1:index + 2].decode("utf-8", "ignore") == "-"):
                
                # If it is a dash, and there was a word preceding it, mark the word complete. Do not imcrement,
                #   as the next call to this function will pick it up.
                if len(word) > 0:
                    word_complete = True
                    
                # Dash with no preceding word, add dash to dictionary, skip to next character
                else:
                    word = "--"
                    word_complete = True
                    index = index + 2

            # Next character is a letter, so it is part of a hyphenated word
            elif index < file_size and is_letter(file_map[index + 1:index + 2].decode("utf-8", "ignore")):
                word = word + char
                index = index + 1

            # Not a hypenated word or dash, just end the word
            else:
                word = word + char
                word_complete = True
                index = index + 1

        # Determine if the character is a punctuation mark
        elif (is_punc(char)):
        
            # If there was a word before the punctuation mark (as length of word > 0), mark the word complete. Do not increment
            #   the index, as the next iteration will pick up the punctuation mark
            if len(word) > 0:
                word_complete = True
            
            # If there is no word before the punctuation mark, the word will be the punctuation mark
            else:
                word = word + char
                word_complete = True
                index = index + 1
        
        # Determine if the character is neither a letter or punctuation mark
        else:
        
            # If the previous character is a letter, end the word
            if (index > 0 and is_letter(file_map[index - 1:index].decode("utf-8", "ignore"))):
                word_complete = True
                index = index + 1
                
            # No previous word, then there is no word
            else:
                word_complete = True
                word = None
                index = index + 1

    return word, index

"""
 This function returns a dictionary of words in the file. The values of the first-level dictionary will
   refer to a second-level dictionary that will contain keys of words that come after it. The values for this
   second level dicitonary will be the number of times the word succeeds the word.

 Our dictionary:
 
 word_dict = { word : { succ_word : number } }
 
 1. word = the word in our text file
 2. succ_word = the word that come immeidately after 'word'
 3. number = number of times the 'succ_word' appeears after 'word'
"""

def get_words(filename):

    # file processing and mapping
    file_object = open(filename, "r+b")
    file_size = Path(filename).stat().st_size
    file_map = mmap.mmap(file_object.fileno(), 0)

    word_dict = {}
    index = 0
    original_element = "" 

    # Iterate through our file to find words
    while (index < file_size):
    
        element, index = get_next_element(file_map, index, file_size)
        
        if element != None:
            
            # First-level dictionary processing
            if not (element in word_dict):
                word_dict.update({element : {}})
        
            # Once athere is a word in our first-level dictionary, the succeeding word will be stored in the
            #   sub-dictionary
            if (len(word_dict) > 1):
                
                # Determine if the word is not already in our second-level dictionary, and process as necessary
                if not (element in word_dict[original_element]):
                    word_dict[original_element].update({element : 1})
                else:
                    value = word_dict[original_element][element]
                    value = value + 1
                    word_dict[original_element][element] = value
                    
            # save word for next iteration
            original_element = element
    
    # Calculate the probabilities of words that come after another word
    for i in word_dict:
    
        total = 0
        
        for j in word_dict[i]:
            total = total + word_dict[i][j]
            
        for k in word_dict[i]:
            probability = word_dict[i][k] / total
            word_dict[i][k] = probability
        
    file_object.close()

    return word_dict;

# This function creates sentences using a markov chain
#   This function creates a sentence from the word dictionary by first randomly
#   selecting a primary word from the word dictionary. Subsequent words are then
#   selected from the second-level dictionary of that particular word, according
#   to their appropriate probabilities.

def create_sentence(word_dict):

    sentence = ""
    word_set = []
    
    # random.choice requires a list
    for key in word_dict.items():
        word_set.append(key[0])
    
    word = random.choice(word_set)
    
    # Ensure the first word is an actual word (no punctuation)
    while not(ord(word[0]) >= 65 and ord(word[0]) <= 90):
        word = random.choice(list(word_set))
        
    # We can begin constructing our sentence
    sentence = sentence + str(word)
    weights = []
    end = False
    period_counter = 0                      # Used to determine how many sentences we want
    prev_word = ""
    
    while end == False:
        sub_word_list = []
        weights = []
        
        # Prepare weights and word list
        for key in word_dict[word].items():
            sub_word_list.append(key[0])
        
        for j in word_dict[word]:
            weights.append(word_dict[word][j])

        word = random.choices(sub_word_list, weights, k=1)[0]
                
        # alternate use
        # word = random.choices(list(word_dict[word].items()), weights, k=1)[0][0]
           
        # Determine is a space is needed
        if is_punc(word) or word == "--":
            sentence = sentence + word
        elif word != "" and word != " ":
            if prev_word == "--":
                sentence = sentence + word
            else:
                sentence = sentence + " " + word
            
        # Sentence limit for output
        if (word == ".") or (word == "?") or (word == "!"):
            period_counter = period_counter + 1
        if period_counter > 0:
            end = True

        prev_word = word
        
    return sentence

def main():

    word_dict = get_words("text.txt")

    print(create_sentence(word_dict))

main()