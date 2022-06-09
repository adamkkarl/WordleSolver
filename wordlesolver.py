#!/bin/python3

import re

wordList = []
words = ""

#keep track of exactly what info we have on the word
green = "....." #found in this position (green)
yellow = ['','','','',''] #found in word but not at this position (yellow)
gray = "" #not found any additional times in the word (gray)

def numMatching():
    """Given all clues so far, return the number of words the answer could be"""
    #narrow down initially based on green letters using regex
    cut1 = re.findall(green, words)

    #narrow down based on yellow letters
    cut2 = list()
    for word in cut1:
        test = True
        for pos in range(5):
            for c in yellow[pos]:
                #test if yellow character IS in word but NOT at this position
                if c in green:
                    letterFoundElseWhere = False
                    for i in range(5):
                        if i != pos and green[i] != c and word[i] == c:
                            #character found in the word
                            letterFoundElseWhere = True
                elif c not in word or word[pos] == c:
                    test = False
        if test == True:
            cut2.append(word)

    #finally, narrow based on grey letters
    #keep in mind that duplicate letters may
    cut3 = list()
    for word in cut2:
        test = True
        for c in gray:
            if c in green:
                for i in range(5):
                    if green[i] != c and word[i] == c:
                        test = False
            elif c in word:
                test = False
        if test == True:
            cut3.append(word)

    print(cut3)
    return len(cut3)


def main():

    f = open(r'sgb-words.txt', 'r')
    wordList = f.readlines()
    numWords = len(wordList)
    print(f"{numWords} 5-letter words in dictionary")
    f.close()

    f = open(r'sgb-words.txt', 'r')
    words = f.read()

    regex = "..ing"
    x = re.findall(regex, words)
    print(f"{len(x)} words match the regex \"{regex}\"")

#    for i in range(numWords):
#        answer = wordList[i]
#        for j in range(numWords):


    f.close()


if __name__ == "__main__":
    main()
