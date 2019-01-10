# Trakt.tv Playback Progress Manager
This is a small Tkinter GUI application that allows a [Trakt.tv](https://trakt.tv) user manage the playback progress items stored in their account.

**[Reddit Post](https://www.reddit.com/r/trakt/comments/95rf3h/playback_progress_manager_python_application/?ref=share&ref_source=link)**

> If you use the scrobbling feature provided by Trakt.tv with your favorite media player (Kodi, for example), and stop in the middle of a movie or episode, it will send the current playback progress (or, how much of the media you watched) to Trakt.tv and store it there.
>
> It can cause some annoyances when syncing the progress back to devices, as currently there's no way (to my knowledge) to remove the playback progress items from Trakt.
>
> I created this small Python application for myself [...] to help me manage those.  

## Supported Python versions
* 2.7
* 3.4
* 3.5
* 3.6
* 3.7

## Python requirements
* [trakt.py](https://github.com/fuzeman/trakt.py)

## Installation
Install requirements:
```shell
pip install -r requirements.txt
```

## Usage
Run `main.pyw`.
```shell
python main.pyw
```
**Note:** If you're using Windows, just double click the file.

## Troubleshooting
* If the application takes some time to load it's usually when Trakt.tv's response is slow, or the site is unavailable.


## Screenshot
![Screenshot](https://user-images.githubusercontent.com/10238474/50993792-2b89ca80-1523-11e9-8736-3a024eaae965.png)
