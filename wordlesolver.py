#!/bin/python3

"""Experiments at determining optimal wordle guesses"""
#from test.libregrtest.save_env import multiprocessing

__author__ = "Adam Karl"

import timeit, array, os, numpy as np
from numpy import uint8, uint16, dtype
from multiprocessing import Process, Queue

PROCESSORS = 4

WORDS_FILE = 'sgb-words.txt'
PATTERN_MATRIX_FILE = 'output_pattern_matrix.txt'
PATTERN_FREQ_MATRIX_FILE = 'output_pattern_freq_matrix.txt'
OUTPUT_FILE = 'output_solution.txt'
patternMatrix = []  # [guessIndex][answerIndex] to find the pattern score
patternFreqMatrix = [] # [guessIndex][patternScore] to find num valid answers

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

def makePatternMatrices():
    """If the pattern matrix exists as a file, import it. Otherwise, generate one and save it to file"""
    if os.path.exists(PATTERN_MATRIX_FILE):
        importPatternMatrix()
    else:
        initializePatternMatrix()

    if os.path.exists(PATTERN_FREQ_MATRIX_FILE):
        importPatternFreqMatrix()
    else:
        initializePatternFreqMatrix()
        
def importPatternMatrix():
    global patternMatrix
    
    print('Importing pattern matrix from file...', end='', flush=True)
    
    startTime = timeit.default_timer()
    
    tmp = list()
    with open(PATTERN_MATRIX_FILE) as file:
        tmp = [[int(n) for n in line.split()] for line in file]
    patternMatrix = np.array(tmp, uint8)
    
    endTime = timeit.default_timer()
    elapsedTime = endTime - startTime
    formatted_time = "{:.2f}".format(elapsedTime)
    print(f'Imported a {patternMatrix.shape[0]} x {patternMatrix.shape[1]} matrix in {formatted_time} sec', flush=True)
    print(patternMatrix)

def initializePatternMatrix():
    """Given the word list, create a 2D matrix of all patterns.
    with gray=0, yellow=1, green=2 at each of 5 positions, the pattern
    can be saved uniquely as an int between 0 and 3^5.
    Use patternMatrix[guessIndex][answerIndex] to find the pattern score"""
    global wordList, numWords, patternMatrix
    
    print('Generating pattern matrix...', flush=True)
    
    startTime = timeit.default_timer()
    
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
            
    endTime = timeit.default_timer()
    elapsedTime = endTime - startTime
    formatted_time = "{:.2f}".format(elapsedTime)
    
    print(f'{numWords}/{numWords} pattern rows generated in {formatted_time} sec', flush=True)

    print(f'Writing pattern matrix to file...', end='', flush=True)
    file = open(PATTERN_MATRIX_FILE, 'w')
    for line in patternMatrix:
        file.write(' '.join(str(x) for x in line))
        file.write('\n')
    file.close()
    print(f'Wrote pattern matrix to file!', flush=True)
    
def importPatternFreqMatrix():
    global patternFreqMatrix
    
    print('Importing pattern freq matrix from file...', end='', flush=True)
    
    startTime = timeit.default_timer()
    
    tmp = list()
    with open(PATTERN_FREQ_MATRIX_FILE) as file:
        tmp = [[int(n) for n in line.split()] for line in file]
    patternFreqMatrix = np.array(tmp, uint16)
    
    endTime = timeit.default_timer()
    elapsedTime = endTime - startTime
    formatted_time = "{:.2f}".format(elapsedTime)
    print(f'Imported a {patternFreqMatrix.shape[0]} x {patternFreqMatrix.shape[1]} matrix in {formatted_time} sec', flush=True)
    print(patternFreqMatrix)
    
def initializePatternFreqMatrix():
    """Given the pattern matrix, create patternFreqMatrix such that
    patternFreqMatrix[guessIndex][patternScore] to find num valid answers.
    In other words, a freq table of the number of answers that produce the given pattern
    when the given guess is tested against them"""
    global numWords, patternMatrix, patternFreqMatrix
    
    print('Generating pattern freq matrix...', end='', flush=True)
    
    tmp = [[0 for j in range(3**5)] for i in range(numWords)]
    patternFreqMatrix = np.array(tmp, dtype=uint16)
    
    startTime = timeit.default_timer()
    
    for i in range(numWords):
        for j in range(numWords):
            pattern = patternMatrix[i][j]
            patternFreqMatrix[i][pattern] += 1
            
    endTime = timeit.default_timer()
    elapsedTime = endTime - startTime
    formatted_time = "{:.2f}".format(elapsedTime)
    print(f"Pattern freq matrix generated in {formatted_time} sec", flush=True)
    
    print(f'Writing pattern freq matrix to file...', end='', flush=True)
    file = open(PATTERN_FREQ_MATRIX_FILE, 'w')
    for line in patternFreqMatrix:
        file.write(' '.join(str(x) for x in line))
        file.write('\n')
    file.close()
    print(f'Wrote pattern freq matrix to file!', flush=True)

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

def analyzeGuessesMultiprocessing(id, Q, numWords, patternMatrix):
    """ALTERNATIVE VERSION OF analyzeGuesses()
    Analyze all combinations of answer and first guess, each time determining
    the number of remaining valid words the answer could be. Return an array of the
    sum total remaining possibilities given an initial guess"""
    remaining = [0 for i in range(numWords)]

    print(f'Proc {id} starting first guess analysis...', flush=True)
    startTime = timeit.default_timer()
    finishedAnswers = 0
    for answerIndex in range(id, numWords, PROCESSORS): #using num processors as the step splits the work evenly
        for firstGuessIndex in range(numWords):
            firstGuessScore = patternMatrix[firstGuessIndex][answerIndex]
            for potentialGuessIndex in range(numWords):
                    #a potential guess could be the answer if
                    #pattern of (prevGuess, answer) == pattern of (prevGuess, potentialGuess)
                    if patternMatrix[firstGuessIndex][potentialGuessIndex] == firstGuessScore:
                        remaining[firstGuessIndex] += 1
            
        finishedAnswers += 1
        if id == PROCESSORS-1:
            #provide progress updates assuming every processor has done as much work as this one
            currTime = timeit.default_timer()
            elapsedTime = currTime - startTime
            predTime = elapsedTime*(numWords/(finishedAnswers*PROCESSORS)) - elapsedTime
            formatted_time = "{:.2f}".format(predTime/60)
            print(f"{finishedAnswers*PROCESSORS}/{numWords} answers analyzed, ~{formatted_time} mins remaining", flush=True)
    Q.put(remaining)

def analyzeGuesses():
    """ALTERNATIVE VERSION OF analyzeGuessesMultiprocessing()
    Analyze all combinations of answer and first guess, each time determining
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

def runAnalysis(multiprocess):
    """Decide whether to use single process or multi process solution
    Return list that indicated total remaining words after a certain guess"""
    global numWords, patternMatrix
    if multiprocess:
        Q = Queue()
        procs = [None for x in range(PROCESSORS)]
        for id in range(PROCESSORS):
            procs[id] = Process(target=analyzeGuessesMultiprocessing, args=(id,Q,numWords,patternMatrix,))
        
        for p in procs:
            p.start()
        for p in procs:
            p.join()
        print("All processes finished", flush=True)
        
        #collate solutions from each process
        Q.put('DONE')
        remaining = [0 for i in range(numWords)]
        while True:
            rem = Q.get()
            if rem=='DONE':
                print(remaining)
                return remaining
            for i in range(numWords):
                remaining[i] += rem[i]
    else:
        return analyzeGuesses()

def main():
    global wordList, numWords, patternMatrix

    loadWordList()
    makePatternMatrices()    
    print(f"{numWords} 5-letter words in dictionary", flush=True)
    
    remaining = runAnalysis(multiprocess = True)
    print(remaining)
    print(f'Writing output solution to file...', flush=True)
    file = open(OUTPUT_FILE, 'w')
    file.write(' '.join(str(x) for x in remaining))
    file.write('\n')
    file.close()
    print(f'Wrote output solution to file!\n', flush=True)
    avgRemaining = [x/numWords for x in remaining]
    
    # print worst word
    worstAvg = max(avgRemaining)
    worstWord = wordList[avgRemaining.index(worstAvg)]
    print(f'{worstWord} is the worst initial guess with an avg of {worstAvg} words remaining\n')
    
    # print top 10 words
    print("TOP 10 INITIAL GUESSES")
    for i in range(10):
        bestAvg = min(avgRemaining)
        bestAveIndex = avgRemaining.index(bestAvg)
        bestWord = wordList[bestAveIndex]
        print(f'{i+1}. {bestWord} with an avg of {bestAvg} words remaining')
        avgRemaining[bestAveIndex] = 9999 #remove this word from further consideration
    
    
def tmp():
    loadWordList()
    makePatternMatrices()

if __name__ == "__main__":
    tmp()