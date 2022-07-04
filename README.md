# WordleSolver

Experiments with a wordle solver

run with 'python wordlesolver.py'

wordle-solutions.txt contains the list of all past & future solution words found at
https://gist.github.com/cfreshman/a7b776506c73284511034e63af1017ee#file-wordle-nyt-answers-alphabetical-txt

wordle-words.txt contains the list of valid wordle guesses found at
https://gist.github.com/prichey/95db6bdef37482ba3f6eb7b4dec99101

wordle-words-adjusted.txt contains the same list as wordle-words.txt but with the list rearranged so that the nth word of wordle-solutions.txt is also the nth word of wordle-words-adjusted.txt.
This allows us to easily keep track of which words in the dictionary are possible solution words.

output_pattern_matrix.txt contains a matrix such that [guessIndex][answerIndex] contains the (ternary) pattern value between 0 and 3^5-1=242

output_pattern_freq_matrix.txt is used for the first guess analysis, and [guessIndex][pattern] contains the frequency of that pattern across the [guessIndex] row of output_pattern_matrix.txt

output_solution.txt is an array that contains the number of remaining solutions after a given first guess. The minimum of this array is located at the index of the initial guess that narrows down the answer the most
