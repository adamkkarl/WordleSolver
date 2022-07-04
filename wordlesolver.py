#!/bin/python3

"""Experiments at determining optimal wordle guesses"""

__author__ = "Adam Karl"

import timeit, array, os, numpy as np
from numpy import uint8, uint16, dtype

ALL_WORDS_FILE = 'wordle-words.txt'
SOLUTION_WORDS_FILE = 'wordle-solutions.txt'

FIRST_GUESS = 'roate'

PATTERN_MATRIX_FILE = 'output_pattern_matrix.txt'
PATTERN_FREQ_MATRIX_FILE = 'output_pattern_freq_matrix.txt'
OUTPUT_FILE = 'output_solution.txt'
        
def loadWordList(file):
    f = open(file, 'r')
    wordList = f.readlines()
    f.close()

    for i in range(len(wordList)): #trim whitespace
        wordList[i] = wordList[i][:5]
    return wordList

def makePatternMatrix(solutionWordList, guessesWordList):
    """If the pattern matrix exists as a file, import it. Otherwise, generate one and save it to file"""
    if os.path.exists(PATTERN_MATRIX_FILE):
        return importPatternMatrix()
    return initializePatternMatrix(solutionWordList, guessesWordList)

def makePatternFreqMatrix(patternMatrix):
    """If the pattern freq matrix exists as a file, import it. Otherwise, generate one and save it to file"""
    if os.path.exists(PATTERN_FREQ_MATRIX_FILE):
        return importPatternFreqMatrix()
    return initializePatternFreqMatrix(patternMatrix)
        
def importPatternMatrix():
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
    return patternMatrix

def initializePatternMatrix(solutionWordList, guessesWordList):
    """Given the word list, create a 2D matrix of all patterns.
    with gray=0, yellow=1, green=2 at each of 5 positions, the pattern
    can be saved uniquely as an int between 0 and 3^5.
    Use patternMatrix[guessIndex][answerIndex] to find the pattern score"""
    print('Generating pattern matrix...', flush=True)
    
    startTime = timeit.default_timer()
    
    tmp = [[0 for _ in range(len(solutionWordList))] for _ in range(len(guessesWordList))]
    patternMatrix = np.array(tmp, dtype=uint8)
    
    for i in range(len(guessesWordList)):
        if i%100 == 0 and i>0:
            print(f'{i}/{len(guessesWordList)} pattern rows generated', flush=True)
        for j in range(len(solutionWordList)):
            guess = guessesWordList[i]
            answer = solutionWordList[j]
            
            pattern = determinePattern(answer, guess)
            score = patternScore(pattern)
            patternMatrix[i][j] = uint8(score)
            
    endTime = timeit.default_timer()
    elapsedTime = endTime - startTime
    formatted_time = "{:.2f}".format(elapsedTime)
    
    print(f'{len(guessesWordList)}/{len(guessesWordList)} pattern rows generated in {formatted_time} sec', flush=True)

    print(f'Writing pattern matrix to file...', end='', flush=True)
    file = open(PATTERN_MATRIX_FILE, 'w')
    for line in patternMatrix:
        file.write(' '.join(str(x) for x in line))
        file.write('\n')
    file.close()
    print(f'Wrote pattern matrix to file!', flush=True)
    
    return patternMatrix
    
def importPatternFreqMatrix():
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
    return patternFreqMatrix
    
def initializePatternFreqMatrix(patternMatrix):
    """Given the pattern matrix, create patternFreqMatrix such that
    patternFreqMatrix[guessIndex][patternScore] to find num valid answers.
    In other words, a freq table of the number of answers that produce the given pattern
    when the given guess is tested against them"""
    print('Generating pattern freq matrix...', end='', flush=True)
    
    tmp = [[0 for _ in range(3**5)] for _ in range(len(patternMatrix))]
    patternFreqMatrix = np.array(tmp, dtype=uint16)
    
    startTime = timeit.default_timer()
    
    for i in range(len(patternMatrix)):
        for j in range(len(patternMatrix[0])):
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
    
    return patternFreqMatrix

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

def analyzeGuesses(allWordsList, patternMatrix, patternFreqMatrix):
    """Analyze all combinations of answer and first guess, each time determining
    the number of remaining valid words the answer could be. Return an array of the
    sum total remaining possibilities given an initial guess"""
    remaining = [0 for _ in range(len(patternMatrix))]

    print('Starting first guess analysis...', flush=True)
    startTime = timeit.default_timer()
    for answerIndex in range(len(patternMatrix[0])):     
        #provide intermittent progress updates
        if answerIndex%100 == 0 and answerIndex > 1:
            currTime = timeit.default_timer()
            elapsedTime = currTime - startTime
            predTime = elapsedTime*(len(patternMatrix[0])/(answerIndex)) - elapsedTime
            formatted_time = "{:.2f}".format(predTime/60)
            lowestRem = min(remaining)
            bestWord = allWordsList[remaining.index(lowestRem)]
            formattedBestRem = "{:.1f}".format(lowestRem/answerIndex)
            print(f"{answerIndex}/{len(patternMatrix[0])} answers analyzed, ~{formatted_time} mins remaining", flush=True)
            print(f'{bestWord} is the best initial guess so far with {formattedBestRem} words remaining\n')
               
        for firstGuessIndex in range(len(patternMatrix)):
            pattern = patternMatrix[firstGuessIndex][answerIndex]
            remaining[firstGuessIndex] += patternFreqMatrix[firstGuessIndex][pattern]

    return remaining

def firstGuessAnalysis():
    """Main driver function to run analysis on the best first guess with no lookahead"""
    # load word lists from file
    allWordsList = loadWordList(ALL_WORDS_FILE)
    solutionWordsList = loadWordList(SOLUTION_WORDS_FILE)
    print(f"{len(allWordsList)} 5-letter words in dictionary", flush=True)
    print(f"{len(solutionWordsList)} of those are possible solutions\n", flush=True)
    
    # use word lists to create pattern matrix and pattern frequency matrix
    patternMatrix = makePatternMatrix(solutionWordsList, allWordsList)
    print(patternMatrix, end='\n\n')
    patternFreqMatrix = makePatternFreqMatrix(patternMatrix)
    print(patternFreqMatrix, end='\n\n')
    
    # use pattern matrices to analyze the best first guess
    remaining = analyzeGuesses(allWordsList, patternMatrix, patternFreqMatrix)

    print(f'Writing output solution to file...', end='', flush=True)
    file = open(OUTPUT_FILE, 'w')
    file.write(' '.join(str(x) for x in remaining))
    file.write('\n')
    file.close()
    print(f'wrote output solution to file!\n', flush=True)
    
    avgRemaining = [x/len(solutionWordsList) for x in remaining]
    
    # print worst word
    worstAvg = max(avgRemaining)
    formattedWorstAvg = "{:.2f}".format(worstAvg)
    worstWord = allWordsList[avgRemaining.index(worstAvg)]
    pctEliminated = "{:.2f}".format(100*(1 - (worstAvg/len(solutionWordsList))))
    print("WORST INITIAL GUESS")
    print(f'{worstWord} is the worst initial guess with an avg of {formattedWorstAvg} words remaining ({pctEliminated}% eliminated)\n')
    
    # print top 10 words
    print("TOP 10 INITIAL GUESSES")
    for i in range(10):
        bestAvg = min(avgRemaining)
        bestAveIndex = avgRemaining.index(bestAvg)
        bestWord = allWordsList[bestAveIndex]
        formattedBestAvg = "{:.2f}".format(bestAvg)
        pctEliminated = "{:.2f}".format(100*(1 - (bestAvg/len(solutionWordsList))))
        print(f'{i+1}. {bestWord} with an avg of {formattedBestAvg} words remaining ({pctEliminated}% eliminated)')
        avgRemaining[bestAveIndex] = 9999 #remove this word from further consideration
        
def optimalRemainingGuesses(answerIndex, possibleSolutionIndices, patternMatrix, solutionWordsList, allWordsList):
    """Given the answer and the remaining pool of possible words, recursively
    determine the number of guesses necessary with optimal play to get the answer"""
    # if only one solution remains, we've found it
    if len(possibleSolutionIndices) == 1:
        if answerIndex != possibleSolutionIndices[0]:
            print(f"ERROR: ANSWER = {solutionWordsList[answerIndex]}; GUESS={solutionWordsList[possibleSolutionIndices[0]]}")
        # print guess
        print(f"{solutionWordsList[answerIndex]} ", end='')
        return 1
    
    # if two solutions remain, guess the first one in alphabetical order
    if len(possibleSolutionIndices) == 2:
        print(f"{solutionWordsList[possibleSolutionIndices[0]]} ", end='')
        if answerIndex == possibleSolutionIndices[0]:
            return 1
        elif answerIndex == possibleSolutionIndices[1]:
            # print guess
            print(f"{solutionWordsList[possibleSolutionIndices[1]]} ", end='')
            return 2
        else:
            print(f"ERROR: ANSWER = {solutionWordsList[answerIndex]}; ", end='')
            print(f"GUESSES = {solutionWordsList[possibleSolutionIndices[0]]}, {solutionWordsList[possibleSolutionIndices[0]]}")
    
    # determine the guess that minimizes the average remaining answers
    bestGuessIndex = -1
    bestGuessRemainingPossibleAnswers = -1  
    for guessIndex in range(len(patternMatrix)):
        patternsDict = dict()
        for potentialAnswerIndex in possibleSolutionIndices:
            pattern = patternMatrix[guessIndex][potentialAnswerIndex]
            if pattern in patternsDict.keys():
                patternsDict[pattern] += 1
            else:
                patternsDict[pattern] = 1
        avgRemainingSolutions = sum(patternsDict.values()) / len(patternsDict) 
        if avgRemainingSolutions < bestGuessRemainingPossibleAnswers or bestGuessIndex == -1:
            bestGuessIndex = guessIndex
            bestGuessRemainingPossibleAnswers = avgRemainingSolutions
            
    # print guess
    print(f"{allWordsList[bestGuessIndex]} ", end='')
    
    # if this guess is  the answer, we've found it
    if allWordsList[bestGuessIndex] == solutionWordsList[answerIndex]:
        # guessed the answer
        return 1
    
    # determine which words are could still be the solution after this guess
    myPossibleSolutionIndices = list()
    for i in possibleSolutionIndices:
        if patternMatrix[bestGuessIndex][i] == patternMatrix[bestGuessIndex][answerIndex]:
            myPossibleSolutionIndices.append(i)
    
    # recursive call
    return 1 + optimalRemainingGuesses(answerIndex, myPossibleSolutionIndices, patternMatrix, solutionWordsList, allWordsList)

        
def main():
    """Driver to simulate solving all possible answers by first guessing 'roate'
    then using the best guessing strategy to minimize total guesses
    """
    # load word lists from file
    allWordsList = loadWordList(ALL_WORDS_FILE)
    solutionWordsList = loadWordList(SOLUTION_WORDS_FILE)
    print(f"{len(allWordsList)} 5-letter words in dictionary", flush=True)
    print(f"{len(solutionWordsList)} of those are possible solutions\n", flush=True)
    
    # use word lists to create pattern matrix and pattern frequency matrix
    patternMatrix = makePatternMatrix(solutionWordsList, allWordsList)
    print(patternMatrix, end='\n\n')
    
    # always guess 'roate' first
    firstGuessIndex = allWordsList.index(FIRST_GUESS)
    
    guessesSum = 0
    for ansIndex in range(len(solutionWordsList)):
        # guess 'roate' first and determine the list of remaining words
        myPossibleSolutionIndices = list()
        for i in range(len(solutionWordsList)):
            if patternMatrix[firstGuessIndex][i] == patternMatrix[firstGuessIndex][ansIndex]:
                myPossibleSolutionIndices.append(i)
        
        # print updates        
        print(f"{ansIndex+1}/{len(solutionWordsList)}: {allWordsList[firstGuessIndex]} ", end='')
        
        # determine number of guesses using optimal strategy
        numGuesses = 1 + optimalRemainingGuesses(ansIndex, myPossibleSolutionIndices, patternMatrix, solutionWordsList, allWordsList)
        guessesSum += numGuesses
    
        print(flush=True)
        
    avgGuesses = guessesSum / len(solutionWordsList) 
    formattedAvgGuesses = "{:.4f}".format(avgGuesses)
    print(f"\nThis strategy uses an average of {formattedAvgGuesses} guesses")

if __name__ == "__main__":
    # firstGuessAnalysis()
    main()