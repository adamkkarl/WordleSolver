#!/bin/python3

"""Experiments at determining optimal wordle guesses"""

__author__ = "Adam Karl"

import timeit, array, os, numpy as np
from numpy import uint8, dtype
from multiprocessing import Process, Queue

PROCESSORS = 1

WORDS_FILE = 'sgb-words.txt'
PATTERN_MATRIX_FILE = 'output_pattern_matrix.txt'
patternMatrix = []  #patternMatrix[guessIndex][answerIndex] to find the pattern score

wordList = []
numWords = 0
remaining = []
        
def loadWordList():
    global wordList, numWords

    f = open(WORDS_FILE, 'r')
    wordList = f.readlines()
    f.close()

    numWords = len(wordList)
    for i in range(numWords): #trim whitespace
        wordList[i] = wordList[i][:5]
    return

def makePatternMatrix():
    """If the pattern matrix exists as a file, import it. Otherwise, generate one and save it to file"""
    if os.path.exists(PATTERN_MATRIX_FILE):
        importPatternMatrix()
    else:
        initializePatternMatrix()
        
def importPatternMatrix():
    global patternMatrix
    
    print('Importing pattern matrix from file...', end='', flush=True)
    
    tmp = list()
    with open(PATTERN_MATRIX_FILE) as file:
        tmp = [[int(n) for n in line.split()] for line in file]
    patternMatrix = np.array(tmp, uint8)
    
    print(f'Imported a {patternMatrix.shape[0]} x {patternMatrix.shape[1]} matrix!', flush=True)

def initializePatternMatrix():
    """Given the word list, create a 2D matrix of all patterns.
    with gray=0, yellow=1, green=2 at each of 5 positions, the pattern
    can be saved uniquely as an int between 0 and 3^5.
    Use patternMatrix[guessIndex][answerIndex] to find the pattern score"""
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
            
            pattern = determinePattern(answer, guess)
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

def determinePattern(answer, guess):
    """Given a guess and answer, determine a pattern for the guess where
    0=gray, 1=yellow, 2=green"""
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
    return pattern

def patternScore(pattern):
    """input: list of 5 integers where 0=gray 1=yellow 2=green
    output: unique int between 0 and 3^5-1"""
    ret = pattern[0]*(3**4) + pattern[1]*(3**3) + pattern[2]*(3**2) + pattern[3]*3 + pattern[4]
    return ret

def analyzeGuesses():
    """Analyze all combinations of answer and first guess, each time determining
    the number of remaining valid words the answer could be. Return an array of the
    sum total remaining possibilities given an initial guess"""
    global wordList, numWords, patternMatrix
    
    remaining = [0 for i in range(numWords)]

    print('Starting first guess analysis...', flush=True)
    startTime = timeit.default_timer()
    for answerIndex in range(numWords):        
        for firstGuessIndex in range(numWords):
            firstGuessScore = patternMatrix[firstGuessIndex][answerIndex]
            for potentialGuessIndex in range(numWords):
                    #a potential guess could be the answer if
                    #pattern of (prevGuess, answer) == pattern of (prevGuess, potentialGuess)
                    if patternMatrix[firstGuessIndex][potentialGuessIndex] == firstGuessScore:
                        remaining[firstGuessIndex] += 1
            
        #provide progress updates
        currTime = timeit.default_timer()
        elapsedTime = currTime - startTime
        predTime = elapsedTime*(numWords/(answerIndex+1)) - elapsedTime
        formatted_time = "{:.2f}".format(predTime/60)
        lowestRem = min(remaining)
        bestWord = wordList[remaining.index(lowestRem)]
        print(f'{bestWord} is the best initial guess so far with {lowestRem/(answerIndex+1)} words remaining')
        print(f"{answerIndex+1}/{numWords} answers analyzed, ~{formatted_time} mins remaining", flush=True)
    return remaining

def main():
    global wordList, numWords, patternMatrix

    loadWordList()
    makePatternMatrix()    
    print(f"{numWords} 5-letter words in dictionary", flush=True)
    
    remaining = analyzeGuesses()
    avgRemaining = [x/numWords for x in remaining]

    bestAvg = min(avgRemaining)
    bestWord = wordList[avgRemaining.index(bestAvg)]
    print(f'{bestWord} is the best initial guess with an avg of {bestAvg} words remaining')
    
    worstAvg = max(avgRemaining)
    worstWord = wordList[avgRemaining.index(worstAvg)]
    print(f'{worstWord} is the worst initial guess with an avg of {worstAvg} words remaining')

if __name__ == "__main__":
    main()