# Games for Babies and Toddlers
Author: Mike Zhong

This project was mostly my attempt to learn pygame as well as develop an application that would be
fun and instructive for my 2-year old, allowing her to bash on my keyboard and click my mouse without
fear of messing up my computer or ordering things online.

## Installation
Super easy install with minimal requirements, virtualenvs are recommended so as to not mess up your
default interpreter and environment.

```
git clone https://github.com/myz540/baby-games.git
cd baby-games
# setup your venv if you so choose
pip install -r requirements.txt
python flashcard_game.py
```

## Available flashcards
The available flashcards were sourced from https://www.eslflashcards.com/

If you want to add your own flashcards, the process is straightforward.
1. Gather your flashcards as PDF or image files (.png, .gif, .jpeg)
2. Tools like `pdfseparate` and `pdftoppm` make this task much easier
3. Create your own subdirectory at `static/flashcards/<your-flashcard-folder>`
4. Launch game and your flashcards will be integrated

## Current features
* Cycles through flashcards with replacement
* Moves to next flashcard on any keyboard button press
* Clicking any mouse button paints a color (random, primary, your choice) to the screen

## Future plans
* See #ToDos
* setup a config file to manage things like screen size and flashcard source directories
  