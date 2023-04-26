# auto-makemkv
Python tool for matching Blu-ray and Video disc files and folders with movies retrieved from the TMDB API, and converting to MKV format with makemkvcon.

This program can either by run normally with ```python3 auto-makemkv.py``` or in auto mode with ```python3 auto-makemkv.py auto```

Normal mode prompts the user for a library path and a destination path and iterates through all Blu-ray and Video folders and images within the library path.
The user is prompted at each step of the process and can manually match each disc with results from TMDB before converting to MKV format.
MKV files are placed in their own named folders within the chosen destination, in the format "Title (Year) for easy organization and matching with programs like Plex or Jellyfin.
A process log is also created which allows the user to automatically skip already processed discs when the program is run again.

Auto mode proceeds through TMDB matching and makemkv conversion without user input, using all default options. This mode is ideal for running as a scheduled task, though it may fail to match movies or produce other unexpected errors.

In either mode, the ```api_key``` variable in ```auto-makemkv.py``` must be set to your TMDB API key. This key is free and easy to obtain from the TMDB website.

In auto mode, the ```lib_path``` and ```dest_path``` variables must also be set to your desired library and destination paths.

You may run into various error messages during the MKV generation process, such as disc read speed messages or errors indicating that no optical drive is detected. You can mostly ignore these, as they are intended for use when ripping from a physcical disc.

Dependencies:

- [makemkvcon](https://forum.makemkv.com/forum/viewtopic.php?t=224) - MakeMKV console tools bundled with a standard MakeMKV install. I would suggest building MakeMKV from source, as the snap store version has permission issues integrating with python-makemkv. [Here's a handy script for easily building MakeMKV from source.](https://github.com/chase-cobb/makemkv-linux-installer-script)
- [makemkv[cli]](https://pypi.org/project/makemkv/) - Python module for running makemkvcon commands.
- [parse-torrent-title](https://pypi.org/project/parse-torrent-title/) - Python module for extracting torrent info from common torrent title formats, before searching TMDB.
- [requests](https://pypi.org/project/requests/) - Python requests module necessary for sending API requests to TMDB.

Python modules can either be installed manually with ```pip install <module-name>```, or automatically using the included ```requirements.txt``` file, by running ```pip install -r requirements.txt```

This script has only been tested on Linux, and would likely need modification to be run on other platforms.
