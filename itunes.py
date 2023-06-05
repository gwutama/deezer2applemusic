#!/usr/bin/env python3

import pyautogui
import psutil
import time
import deezer
import re


class ItunesMacroControl(object):
    Path = '/Applications/iTunes.app/Contents/MacOS/iTunes'
    MousePos = {
        'searchBox': (740, 120),
        'appleMusicSearchButton': (889, 166),
        'firstSongResult': (467, 560),
        'contextAddToLibrary': (467, 551),
        'menuBrowse': (554, 160),
    }

    def __init__(self):
        self._proc = None
        pass

    def start(self):
        if self.is_started() is False:
            self._proc = psutil.Popen([ItunesMacroControl.Path])
            time.sleep(5)

    def stop(self):
        if self.is_started() is True:
            self._proc.terminate()

    def is_started(self):
        for proc in psutil.process_iter():
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if pinfo['name'] == 'iTunes':
                self._proc = proc
                return True
        return False

    def bring_forward(self):
        if self.is_started() is False:
            return False
        # execute AppleScript
        # http://stackoverflow.com/questions/34705575/python-activate-window-in-os-x
        cmd = 'tell application "iTunes" to activate'
        psutil.Popen(['osascript', '-e', cmd])
        return True

    def resize(self):
        if self.is_started() is False:
            return False
        # execute AppleScript
        # http://alvinalexander.com/source-code/mac-os-x/how-size-or-resize-application-windows-applescript
        cmd = """
tell application "iTunes"
    set bounds of front window to {100, 100, 800, 800}
end tell
"""
        psutil.Popen(['osascript', '-e', cmd])
        return True

    def position_mouse(self, pos):
        if self.is_started() is False:
            return False
        pyautogui.moveTo(ItunesMacroControl.MousePos[pos])

    def mouse_click(self, pos, button):
        if self.is_started() is False:
            return False
        pyautogui.click(ItunesMacroControl.MousePos[pos][0], ItunesMacroControl.MousePos[pos][1], button=button)

    def input_textbox(self, pos, text):
        if self.is_started() is False:
            return False
        pyautogui.moveTo(ItunesMacroControl.MousePos[pos])
        pyautogui.typewrite(text)
        pyautogui.press('enter')

    # --------------------------------------------------------------------------
    # HIGH LEVEL MACROS START HERE
    # --------------------------------------------------------------------------

    def activate_window(self):
        self.resize()
        self.bring_forward()
        time.sleep(1)

    def activate_menu(self, menu):
        self.position_mouse(menu)
        self.mouse_click(menu, 'left')
        time.sleep(1)

    def search_apple_music(self, term):
        self.activate_window()
        self.position_mouse('searchBox')
        self.mouse_click('searchBox', 'left')
        self.position_mouse('appleMusicSearchButton')
        self.mouse_click('appleMusicSearchButton', 'left')
        self.input_textbox('searchBox', term)
        time.sleep(5)

    def add_track_into_library(self):
        self.position_mouse('firstSongResult')
        self.mouse_click('firstSongResult', 'left')
        self.position_mouse('contextAddToLibrary')
        self.mouse_click('contextAddToLibrary', 'left')
        time.sleep(1)
        pyautogui.press('enter') # allow double
        time.sleep(1)


class DeezerPlaylist(object):
    def __init__(self):
        self._client = deezer.Client()

    def tracks(self, playlist_id):
        playlist = self._client.get_playlist(playlist_id)
        return playlist.nb_tracks, playlist.tracks


if __name__ == '__main__':
    it = ItunesMacroControl()
    it.start()
    it.activate_window()
    it.activate_menu('menuBrowse')

    playlist = DeezerPlaylist()
    num_tracks, tracks = playlist.tracks(1629645365)
    i = 1

    for track in tracks:
        term = "%s %s" % (track.artist.name, track.title_short)
        # remove everything in parenthesis "()"
        term = re.sub(r'\([^)]*\)', '', term)
        print("[%s/%s] adding: %s" % (i, num_tracks, term))
        it.search_apple_music(term)
        it.add_track_into_library()
        i += 1
