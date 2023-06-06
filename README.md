Generates possible guesses for the wordle!

*Currently throws an infinite loop! Debugging in progress*

Example:

![alt text](example_guess.png?raw=true)

Use the `-g` flag to indicate green letters; use the `-y` flag to indicate yellow letters.
Each letter may be followed by multiple indices to handle duplicate letters.

This guess would be entered as:

	-g o 2 u 3 -y t 5

This will return all viable guesses containing *o* at position 2, a *u* at position 3, and a *t* at any position other than 5:

	possible guesses: {'tough', 'route', 'pouty', 'mouth', 'youth', 'south', 'touch'}

Enter 'found' to quit.

Happy wordling!
