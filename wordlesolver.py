#!/bin/python3

"""Experiments at determining optimal wordle guesses"""

__author__ = "Adam Karl"

import timeit
from multiprocessing import Process, Queue

PROCESSORS = 8
answersTested = 0

wordList = []
numWords = 0

#example: first guess 'owing' when answer is 'wring'
#guessed = ['owing','','','','', '']
#colors  = [[0,1,2,2,2],None, None, None, None, None]

def validBasedOnGuess(myWord, prevGuess, colors):
    """given a word and a single previous guess + corresponding colors,
    return true if the word could possibly be a solution"""
    word = myWord

    #check word matches green letters
    greenIndexes = list()
    for pos in range(5):
        if colors[pos] == 2:
            greenIndexes.append(pos)
            if word[pos] != prevGuess[pos]:
                #doesn't match green letter
                return False

    #since all greens match, can eliminate to make problem simpler
    while len(greenIndexes) > 0:
        i = greenIndexes[-1]
        word = word[:i] + word[i+1:]
        prevGuess = prevGuess[:i] + prevGuess[i+1:]
        del colors[i]
        del greenIndexes[-1]

    #solve yellows by iteratively simplifying yellow pairs
    #replace yellow char in prevGuess with '?'
    #replace first instance of that char in word with '!'
    for pos in range(len(prevGuess)):
        if colors[pos] == 1:
            c = prevGuess[pos]
            restOfWord = word[:pos] + word[pos+1:]
            if c not in restOfWord or word[pos] == c:
                #yellow letter either found in same position or not at all
                return False
            else:
                prevGuess = prevGuess[:pos] + '?' + prevGuess[pos+1:]
                wordPos = word.find(c)
                word = word[:wordPos] + '!' + word[wordPos+1:]


    #finally, check for overlap in gray characters
    for pos in range(len(prevGuess)):
        if colors[pos] == 0:
            if prevGuess in word:
                return False

    return True


def numRemainingValidWords(answer, guessed, colors):
    """Given all clues so far, return the number of words the answer could still be"""
    global wordList

    if guessed[0] == None:
        #no guesses made yet so whole dictionary is valid
        return wordList

    remaining = list()
    for word in wordList:
        valid = True
        for i in range(6):
            if guessed[i] == None:
                break
            elif validBasedOnGuess(word, guessed[i], colors[i].copy()) == False:
                    valid = False
                    break
        if valid:
            remaining.append(word)

    return len(remaining)

def analyzeGuessesGivenAnswer(answer):
    """Given the answer, try all possible initial guesses and determine how
    much they narrow down the solution. Add to global based on the remaining
    solutions"""
    global wordList, numWords

    remaining = [0 for i in range(numWords)]

    for i in range(numWords):
        firstGuess = wordList[i]
        c = determineColors(answer, firstGuess)
        guessed = [firstGuess, None, None, None, None, None]
        colors  = [c, None, None, None, None, None]
        rem = numRemainingValidWords(answer, guessed, colors)
        remaining[i] += rem
    return remaining


def determineColors(answer, guess):
    """given the answer and a guess, determine the colors of the letters
    output is an array of 5 values, 0=gray, 1=yellow, 2=green"""
    #start with all letters grayed out
    colors = [0,0,0,0,0]

    #determine greens
    for pos in range(5):
        if guess[pos] == answer[pos]:
            colors[pos] = 2

    #determine yellows
    #for each position that isn't already green, the first occurrance of the character
    #that isn't yellow or green should be changed to yellow
    for pos in range(5):
        if colors[pos] != 2:
            c = answer[pos]
            for i in range(5):
                if colors[i] == 0 and guess[i] == c:
                    colors[i] = 1
                    break
    return colors

def multiprocessAnalysis(id,Q):
    loadFile()
    remaining = [0 for _ in range(numWords)]
    for i in range(id, numWords, PROCESSORS):
        answer = wordList[i]
        tmp = analyzeGuessesGivenAnswer(answer)
        for j in range(numWords):
            remaining[j] += tmp[j]
        print(f"finished {answer}", flush=True)

    Q.put(remaining) #push to queue so that master process collects data
    return

def loadFile():
    global wordList, numWords

    f = open(r'sgb-words.txt', 'r')
    wordList = f.readlines()
    f.close()

    numWords = len(wordList)
    for i in range(numWords): #trim whitespace
        wordList[i] = wordList[i][:5]
    return


def main():
    global wordList, numWords
    Q = Queue()

    loadFile()
    remaining = [0 for i in range(numWords)]

    print(f"{numWords} 5-letter words in dictionary", flush=True)


    procs = [None for x in range(PROCESSORS)]
    for id in range(PROCESSORS):
        procs[id] = Process(target=multiprocessAnalysis, args=(id,Q,))

    print(f"proc {id}")
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print("All processes finished", flush=True)

    #gather data each process has returned
    Q.put('DONE')
    while True:
        rem = Q.get()
        if rem=='DONE':
            break
        for i in range(numWords):
            remaining[i] += rem[i]

    avgRemaining = [x/numWords for x in remaining]

    bestAvg = min(avgRemaining)
    bestWord = wordList[avgRemaining.index(bestAvg)]
    print(f'{bestWord} is the best initial guess with an avg of {bestAvg} words remaining')

if __name__ == "__main__":
    main()
