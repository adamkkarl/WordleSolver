#!/bin/python3

import re

wordList = []
numWords = 0

answer = ''
guessed = [None, None, None, None, None, None] # holds the 5-letter guessed
colors  = [None, None, None, None, None, None] # 0=gray, 1=yellow, 2=green

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


def remainingValidWords():
    """Given all clues so far, return the words the answer could still be"""
    global wordList, guessed, colors

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

    return remaining

def guess(myGuess, numGuess):
    """add the given word to the list of guessed and determine the colors of the letters
    input: the word and the guess number (0 for first guess up to 5 for 6th and final guess)"""
    global guessed, colors, answer

    guessed[numGuess] = myGuess
    tmp = [0,0,0,0,0] #start with all letters grayed out

    #determine greens
    for pos in range(5):
        if myGuess[pos] == answer[pos]:
            tmp[pos] = 2

    #determine yellows
    #for each position that isn't already green, the first occurrance of the character
    #that isn't yellow or green should be changed to yellow
    for pos in range(5):
        if tmp[pos] != 2:
            c = answer[pos]
            for i in range(5):
                if tmp[i] == 0 and myGuess[i] == c:
                    tmp[i] = 1
                    break

    colors[numGuess] = tmp
    return

def resetGuesses():
    guessed = [None, None, None, None, None, None] # holds the 5-letter guessed
    colors  = [None, None, None, None, None, None] # 0=gray, 1=yellow, 2=green

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
    global wordList, numWords, answer

    loadFile()

    print(f"{numWords} 5-letter words in dictionary", flush=True)

    f = open(r'sgb-words.txt', 'r')
    words = f.read()

    remaining = [0 for i in range(numWords)]
    for i in range(numWords):
        answer = wordList[i]
        print(f"{i}/{numWords} complete", flush=True)
        for j in range(numWords):
            resetGuesses()
            guess(wordList[j], 0)
            remaining[j] += len(remainingValidWords())

    avgRemaining = [x/numWords for x in remaining]

    bestAvg = min(avgRemaining)
    bestWord = wordList[avgRemaining.index(bestAvg)]
    print(f'{bestWord} is the best initial guess with an avg of {bestAvg} words remaining')

    f.close()

if __name__ == "__main__":
    main()
