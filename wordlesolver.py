#!/bin/python3

import re

wordList = []
numWords = 0

answer = ''
guesses = ['','','','','', ''] # holds the 5-letter guesses
colors  = [None, None, None, None, None, None] # 0=gray, 1=yellow, 2=green

#example: first guess 'owing' when answer is 'wring'
#guesses = ['owing','','','','', '']
#colors  = ['01222','','','','', '']

def numMatching():
    """Given all clues so far, return the number of words the answer could be"""
    global wordList, numWords

    remaining = list()
    for word in wordList:
        valid = True
        for guess in guesses:
            for pos in range(5):
                if valid:
                    if guess[pos] == '2' and word[pos] != guess[pos]:
                        #guess doesn't match established green
                        valid = False
                    elif guess[pos] == '1':
                        #guess has inva
                        pass


        if valid:
            remaining.append(word)

    print(remaining)
    print(f"{len(remaining)}", flush=True)
    return len(remaining)

def guess(myGuess, numGuess):
    """add the given word to the list of guesses and determine the colors of the letters
    input: the word and the guess number (0 for first guess up to 5 for 6th and final guess)"""
    global guesses, colors, answer

    guesses[numGuess] = myGuess
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

    print(f"{numWords} 5-letter words in dictionary")

    f = open(r'sgb-words.txt', 'r')
    words = f.read()
    print(words, flush=True)

    remaining = [0 for i in range(numWords)]
    # for i in range(numWords):
    #     answer = wordList[i]
    #     for j in range(numWords):
    #         guess = wordList[j]
    #         green = ''
    #         yellow = ['a','','','','']
    #         gray = ''
    #         for pos in range(5):
    #             #determine greens
    #             if answer[pos] == guess[pos]:
    #                 green = green + answer[pos]
    #             else:
    #                 green = green + '.'
    #
    #             #determine yellows
    #             if guess[pos] != answer[pos] and guess[pos] in answer:
    #                 yellow[pos] = yellow[pos] + guess[pos]
    #
    #             #determine grays
    #             if guess[pos] not in guess:
    #                 gray = gray + guess[pos]
    #
    #         avgRemaining[j] += numMatching()

    avgRemaining = [x/numWords for x in remaining]

    bestAvg = min(avgRemaining)
    bestWord = wordList[avgRemaining.index(bestAvg)]

    print(f'{bestWord} is the best initial guess with an avg of {bestAvg} words remaining')


    f.close()


def tmp():
    global answer, guesses, colors

    loadFile()

    answer = 'aaaxx'
    guess('xxxhh', 0)
    print(guesses)
    print(colors)


if __name__ == "__main__":
    main()
