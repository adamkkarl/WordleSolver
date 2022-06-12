#!/bin/python3

"""Experiments at determining optimal wordle guesses"""

__author__ = "Adam Karl"

import timeit, array, os
import numpy as np
from numpy import uint8, dtype

WORDS_FILE = 'sgb-words.txt'
PATTERN_MATRIX_FILE = 'output_pattern_matrix.txt'
patternMatrix = []

wordList = []
numWords = 0
remaining = []

# def validBasedOnGuess(myWord, prevGuess, colors):
#     """given a word and a single previous guess + corresponding colors,
#     return true if the word could possibly be a solution"""
#     word = myWord
#
#     #check word matches green letters
#     greenIndexes = list()
#     for pos in range(5):
#         if colors[pos] == 2:
#             greenIndexes.append(pos)
#             if word[pos] != prevGuess[pos]:
#                 #doesn't match green letter
#                 return False
#
#     #since all greens match, can eliminate to make problem simpler
#     while len(greenIndexes) > 0:
#         i = greenIndexes[-1]
#         word = word[:i] + word[i+1:]
#         prevGuess = prevGuess[:i] + prevGuess[i+1:]
#         del colors[i]
#         del greenIndexes[-1]
#
#     #solve yellows by iteratively simplifying yellow pairs
#     #replace yellow char in prevGuess with '?'
#     #replace first instance of that char in word with '!'
#     for pos in range(len(prevGuess)):
#         if colors[pos] == 1:
#             c = prevGuess[pos]
#             restOfWord = word[:pos] + word[pos+1:]
#             if c not in restOfWord or word[pos] == c:
#                 #yellow letter either found in same position or not at all
#                 return False
#             else:
#                 prevGuess = prevGuess[:pos] + '?' + prevGuess[pos+1:]
#                 wordPos = word.find(c)
#                 word = word[:wordPos] + '!' + word[wordPos+1:]
#
#
#     #finally, check for overlap in gray characters
#     for pos in range(len(prevGuess)):
#         if colors[pos] == 0:
#             if prevGuess in word:
#                 return False
#
#     return True
#
#
# def numRemainingValidWords(answer, guessed, colors):
#     """Given all clues so far, return the number of words the answer could still be"""
#     global wordList
#
#     if guessed[0] == None:
#         #no guesses made yet so whole dictionary is valid
#         return wordList
#
#     remaining = list()
#     for word in wordList:
#         valid = True
#         for i in range(6):
#             if guessed[i] == None:
#                 break
#             elif validBasedOnGuess(word, guessed[i], colors[i].copy()) == False:
#                     valid = False
#                     break
#         if valid:
#             remaining.append(word)
#
#     return len(remaining)
#
# def analyzeGuessesGivenAnswer(answer):
#     """Given the answer, try all possible initial guesses and determine how
#     much they narrow down the solution. Add to global based on the remaining
#     solutions"""
#     global wordList, numWords, remaining
#
#     for i in range(numWords):
#         firstGuess = wordList[i]
#         c = determineColors(answer, firstGuess)
#         guessed = [firstGuess, None, None, None, None, None]
#         colors  = [c, None, None, None, None, None]
#         rem = numRemainingValidWords(answer, guessed, colors)
#         remaining[i] += rem
#
#
# def determineColors(answer, guess):
#     """given the answer and a guess, determine the colors of the letters
#     output is an array of 5 values, 0=gray, 1=yellow, 2=green"""
#     #start with all letters grayed out
#     colors = array.array('i', (0 for i in range(5)))
#
#
#     #determine greens
#     for pos in range(5):
#         if guess[pos] == answer[pos]:
#             colors[pos] = 2
#
#     #determine yellows
#     #for each position that isn't already green, the first occurrence of the character
#     #that isn't yellow or green should be changed to yellow
#     for pos in range(5):
#         if colors[pos] != 2:
#             c = answer[pos]
#             for i in range(5):
#                 if colors[i] == 0 and guess[i] == c:
#                     colors[i] = 1
#                     break
#     return colors

def patternScore(colors):
    """input: list of 5 integers where 0=gray 1=yellow 2=green
    output: unique int between 0 and 3^5-1"""
    n = colors[0]*(3**4) + colors[1]*(3**3) + colors[2]*(3**2) + colors[3]*3 + colors[4]
    return n


def initializePatternMatrix():
    """Given the word list, create a 2D matrix of all patterns.
    with gray=0, yellow=1, green=2 at each of 5 positions, the pattern
    can be saved uniquely as an int between 0 and 3^5.
    Use colorMatrix[guess][answer] to find the pattern"""
    global wordList, numWords, patternMatrix
    
    print('Generating pattern matrix...', flush=True)
    
    tmp = [[0 for i in range(numWords)] for j in range(numWords)]
    patternMatrix = np.array(tmp, dtype=uint8)
    
    
    for i in range(numWords):
        if i%100 == 0 and i>0:
            print(f'{i}/{numWords} pattern rows generated', flush=True)
        for j in range(numWords):
            guess = wordList[i]
            answer = wordList[j]
            pattern = [0,0,0,0,0]

            #determine greens
            for pos in range(5):
                if guess[pos] == answer[pos]:
                    pattern[pos] = 2

            #determine yellows
            #for each answer char that isn't already green, the *first* occurrence of the
            #guess char that isn't yellow or green should be changed to yellow
            for ansPos in range(5):
                if pattern[ansPos] != 2:
                    c = answer[ansPos]
                    for guessPos in range(5):
                        if pattern[guessPos] == 0 and guess[guessPos] == c:
                            pattern[guessPos] = 1
                            break
            score = patternScore(pattern)
            patternMatrix[i][j] = uint8(score)
    
    print(f'{numWords}/{numWords} pattern rows generated', flush=True)

    print(f'Writing pattern matrix to file...', flush=True)
    file = open(PATTERN_MATRIX_FILE, 'w')
    for line in patternMatrix:
        file.write(' '.join(str(x) for x in line))
        file.write('\n')
    file.close()
    print(f'Wrote pattern matrix to file!', flush=True)

def importPatternMatrix():
    global patternMatrix
    
    print('Importing pattern matrix from file...', end='', flush=True)
    
    tmp = list()
    with open(PATTERN_MATRIX_FILE) as file:
        tmp = [[int(n) for n in line.split()] for line in file]
    patternMatrix = np.array(tmp, uint8)
    
    print(f'Imported a {patternMatrix.shape[0]} x {patternMatrix.shape[1]} matrix!', flush=True)
    
def makePatternMatrix():
    """If the pattern matrix exists as a file, import it. Otherwise, generate one and save it to file"""
    if os.path.exists(PATTERN_MATRIX_FILE):
        importPatternMatrix()
    else:
        initializePatternMatrix()
        
def loadWordList():
    global wordList, numWords

    f = open(WORDS_FILE, 'r')
    wordList = f.readlines()
    f.close()

    numWords = len(wordList)
    for i in range(numWords): #trim whitespace
        wordList[i] = wordList[i][:5]
    return

def main():
    global wordList, numWords, patternMatrix

    loadWordList()
    remaining = [0 for i in range(numWords)]

    print(f"{numWords} 5-letter words in dictionary", flush=True)

    startTime = timeit.default_timer()
    for i in range(numWords):
        answer = wordList[i]
        analyzeGuessesGivenAnswer(answer)

        endTime = timeit.default_timer()
        predTime = (endTime-startTime)*(numWords/(i+1))
        formatted_time = "{:.2f}".format(predTime/3600)
        print(f"{i+1}/{numWords} complete, ~{formatted_time} h remaining", flush=True)

    avgRemaining = [x/numWords for x in remaining]

    bestAvg = min(avgRemaining)
    bestWord = wordList[avgRemaining.index(bestAvg)]
    print(f'{bestWord} is the best initial guess with an avg of {bestAvg} words remaining')
    


def tmp():
    loadWordList()
    startTime = timeit.default_timer()
    makePatternMatrix()
    endTime = timeit.default_timer()
    print(patternMatrix)
    print(f"complete, ~{(endTime-startTime)/60} m elapsed", flush=True)

if __name__ == "__main__":
    tmp()