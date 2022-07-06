#!/bin/python3

"""Experiments at datermining optimal wordle strategy"""

__author__ = "Adam Karl"

import timeit, array, os, numpy as np
from numpy import uint8, uint16, dtype

ALL_WORDS_FILE = '.\input\wordle-words-adjusted.txt'
SOLUTION_WORDS_FILE = '.\input\wordle-solutions.txt'

FIRST_GUESS = 'roate'

GUESS_ESTIMATION_ARRAY = '.\output\output_guess_estimation.txt'
PATTERN_MATRIX_FILE = '.\output\output_pattern_matrix.txt'
PATTERN_FREQ_MATRIX_FILE = '.\output\output_pattern_freq_matrix.txt'
OUTPUT_FILE = '.\output\output_solution.txt'
        
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

def makePatternFreqMatrix(patternMatrix):
    """If the pattern freq matrix exists as a file, import it. Otherwise, generate one and save it to file"""
    if os.path.exists(PATTERN_FREQ_MATRIX_FILE):
        return importPatternFreqMatrix()
    return initializePatternFreqMatrix(patternMatrix)
    
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

def importGuessEstimationArray(length):
    """If the guess estimation array file exists, import it. Otherwise, initialize a blank one
    guessEstimation[n][0] contains an evidence-based estimation of how many guesses is necessary
    to find which of n possible solutions is correct
    guessEstimation[n][1] contains the number of scenarios that have combined to reach that average"""
    if os.path.exists(GUESS_ESTIMATION_ARRAY):
        print(f'Importing guess estimation array...', end='', flush=True)
        f = open(GUESS_ESTIMATION_ARRAY, 'r')
        lines = f.readlines()
        f.close()
        
        guessEstArray = list()
        for line in lines:
            avg, count = line.strip().split()
            guessEstArray.append([float(avg), int(count)])

        print(f'imported a {len(guessEstArray)} x {len(guessEstArray[0])} matrix', flush=True)
        return guessEstArray
    else:
        print(f'Generating blank guess estimation array',  flush=True)
        estArray = [[0.0, 0] for _ in range(length)]
        estArray[1] = [1.0, 1] # one possible word = 1 guess
        estArray[2] = [1.5, 1] # two possible words = 1.5 guesses on avg
        return estArray
     
def saveGuessEstimationArray(guessEstArray):
    """Save the guess estimation array to file"""
    file = open(GUESS_ESTIMATION_ARRAY, 'w')
    for avg, count in guessEstArray:
        file.write(str(avg) + ' ' + str(count) + '\n')
    file.close()
    
def updateGuessEstimationArray(numSolutions, numGuesses, guessEstArray):
    """Given the number of guesses it took to solve a certain number of solutions,
    update the current best estimate"""
    currAvg, count = guessEstArray[numSolutions]
    newAvg = (currAvg * count + numGuesses) / (count + 1)    
    guessEstArray[numSolutions] = [newAvg, count+1]

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
        
def isHardModeGuessBetter(initialSetSize, hardModeAvgSize, nonHardModeAvgSize, guessEstArray):
    """Given avg set sizes for hard and non-hard mode guesses,
    return True if the solver should make the hard mode guess.
    This uses the guessEstArray which gets better the more information is fed in
    
    This function will choose the hard mode guess unless there's evidence to suggest
    the non-hard mode guess is significantly better
    """
    hardModeFloor = int(hardModeAvgSize)
    nonHardModeFloor = int(nonHardModeAvgSize)
    if guessEstArray[hardModeFloor][1] != 0 and guessEstArray[hardModeFloor+1][1] != 0:
        if guessEstArray[nonHardModeFloor][1] != 0 and guessEstArray[nonHardModeFloor+1][1] != 0:
            hardModeDecimal = hardModeAvgSize - hardModeFloor
            hardModeFurtherExpectedGuesses = (1-hardModeDecimal) * guessEstArray[hardModeFloor][0] + hardModeDecimal * guessEstArray[hardModeFloor+1][0]
            hardModeExpectedGuesses = 1 + ((initialSetSize-1)/initialSetSize) * hardModeFurtherExpectedGuesses
            
            nonHardModeDecimal = nonHardModeAvgSize - nonHardModeFloor
            nonHardModeFurtherExpectedGuesses = (1-nonHardModeDecimal) * guessEstArray[nonHardModeFloor][0] + nonHardModeDecimal * guessEstArray[nonHardModeFloor+1][0]
            nonHardModeExpectedGuesses = 1 + nonHardModeFurtherExpectedGuesses
            
            # print scores for the 2 approaches
            # formattedHard = "{:.3f}".format(hardModeExpectedGuesses)
            # formattedNonHard = "{:.3f}".format(nonHardModeExpectedGuesses)
            # print(f'{formattedHard}v{formattedNonHard} ', end='')
            
            if hardModeExpectedGuesses > nonHardModeExpectedGuesses:
                # print('e-', end='')
                return False
    # print('h-', end='')
    return True

def makeBestGuess(answerIndex, possibleSolutionIndices, patternMatrix, guessEstArray, allWordsList):
    """Given the subset of words that can still be the solution, 
    implement a strategy to make the best guess, then continue until the solution is found.
    Return the number of guesses needed to reach the solution"""
    # if only one solution remains, we've found it
    if len(possibleSolutionIndices) == 1:
        print(f"{allWordsList[possibleSolutionIndices[0]]} ", end='')
        return 1
    
    # if two solutions remain, guess one arbitrarily, then the other (if necessary)
    if len(possibleSolutionIndices) == 2:
        print(f"{allWordsList[possibleSolutionIndices[0]]} ", end='')
        if answerIndex == possibleSolutionIndices[0]:
            return 1
        else:
            print(f"{allWordsList[possibleSolutionIndices[1]]} ", end='')
            return 2
    
    # 3+ words remain, so we have to weigh two strategies
    # 1. making a "hard mode" guess to potentially get the answer right this turn
    # 2. guessing a word that cannot be the right answer, but might narrow down the potential solutions better than #1
    
    # 1. find the best 'hard mode' guess. this is based on avg solution set size, not perfectly solved
    hardModeGuessIndex = -1
    hardModeGuessAvgRemSetSize = -1
    for guessIndex in possibleSolutionIndices:
        patternsDict = dict()
        for solutionIndex in possibleSolutionIndices:
            pattern = patternMatrix[guessIndex][solutionIndex]
            if pattern in patternsDict.keys():
                patternsDict[pattern] += 1
            else:
                patternsDict[pattern] = 1
        avgRemainingSetSize = sum(patternsDict.values()) / len(patternsDict) 
        if avgRemainingSetSize < hardModeGuessAvgRemSetSize or hardModeGuessAvgRemSetSize == -1:
            hardModeGuessIndex = guessIndex
            hardModeGuessAvgRemSetSize = avgRemainingSetSize  
            
    # 2. find the best 'non-hard mode' guess. this is based on avg solution set size, not perfectly solved
    nonHardModeGuessIndex = -1
    nonHardModeGuessAvgRemSetSize = -1
    for guessIndex in range(len(patternMatrix)):
        patternsDict = dict()
        for solutionIndex in possibleSolutionIndices:
            pattern = patternMatrix[guessIndex][solutionIndex]
            if pattern in patternsDict.keys():
                patternsDict[pattern] += 1
            else:
                patternsDict[pattern] = 1
        avgRemainingSetSize = sum(patternsDict.values()) / len(patternsDict) 
        if avgRemainingSetSize < nonHardModeGuessAvgRemSetSize or nonHardModeGuessAvgRemSetSize == -1:
            nonHardModeGuessIndex = guessIndex
            nonHardModeGuessAvgRemSetSize = avgRemainingSetSize
    
    # decide between hard mode and non-hard mode
    finalGuessIndex = -1
    if isHardModeGuessBetter(len(possibleSolutionIndices), hardModeGuessAvgRemSetSize, nonHardModeGuessAvgRemSetSize, guessEstArray) == True:
        # make the hard mode guess
        finalGuessIndex = hardModeGuessIndex
    else:
        # make the non-hard mode guess
        finalGuessIndex = nonHardModeGuessIndex
    
    # print guess
    print(f"{allWordsList[finalGuessIndex]} ", end='')
    
    
    solutionGuesses = 0
    # check if we accidentally guessed the word
    if finalGuessIndex == answerIndex:
        solutionGuesses = 1
    else:
        # make guess and narrow down possible solutions
        myPossibleSolutionIndices = list()
        pattern = patternMatrix[finalGuessIndex][answerIndex]
        for index in possibleSolutionIndices:
            if patternMatrix[finalGuessIndex][index] == pattern:
                myPossibleSolutionIndices.append(index)
                
        # use recursive step to solve
        solutionGuesses = 1 + makeBestGuess(answerIndex, myPossibleSolutionIndices, patternMatrix, guessEstArray, allWordsList)
    
    # update estimates of guesses to solve based on solution space
    updateGuessEstimationArray(len(possibleSolutionIndices), solutionGuesses, guessEstArray)
    
    return solutionGuesses
        
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
    
    # import guess estimation array to help estimate best strategy based on remaining possible solutions
    guessEstArray = importGuessEstimationArray(len(solutionWordsList) + 1)
    
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
        print(f"{ansIndex+1}/{len(solutionWordsList)} {allWordsList[ansIndex]}: {allWordsList[firstGuessIndex]} ", end='')
        
        # determine number of guesses using the implemented strategy
        numGuesses = 1 + makeBestGuess(ansIndex, myPossibleSolutionIndices, patternMatrix, guessEstArray, allWordsList)
        guessesSum += numGuesses

        # flush recursive print statements      
        print(flush=True)
        
    # save guess estimation array to improve future guesses based on remaining possible solutions
    saveGuessEstimationArray(guessEstArray)
        
    totalAvgGuesses = guessesSum / len(solutionWordsList) 
    formattedAvgGuesses = "{:.4f}".format(totalAvgGuesses)
    print(f"\nThis strategy uses an average of {formattedAvgGuesses} guesses")

if __name__ == "__main__":
    # firstGuessAnalysis()
    main()
        