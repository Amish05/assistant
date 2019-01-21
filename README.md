# assistant
Virtual assistant written in python

### How to use

Run `main.py` in any working directory and it should work!

### Features:
- timer
- renaming files
- weather in city
- weather in your location (by IP)
- opening web browser
- language switcher (no need to edit `language.txt`)

### Commands:
- timer - `(set )?timer (to )? [0-9]+ .+` - example: `set timer 5 min`
- rename file - `rename .+ to .+` - example: `rename foo.txt to bar.txt`
- exit - `exit`, `quit`, `stop` - example: `quit`
- weather in city - `(what is )?(the )?weather (in )?.+` - example: `weather in London`
- weather in your location - `(what is )?(the )?weather` - example: `what is weather`
- switching language - `language .+` - example: `language english`

**Note**: commands (not examples) are written here in regex

### Extension system

If you want to install an extension, just copy/paste it into `extensions` directory.

### Changing language

If you want to switch language, put language file into `languages` directory and change contents of `language.txt` file to name of your language file (without .json extension) or use language switcher (builtin command).

### Builtin languages:
- English
- Slovak
