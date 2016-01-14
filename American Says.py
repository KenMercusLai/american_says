# -*- coding:utf-8 -*-  
# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from anki.hooks import addHook

import urllib2
from HTMLParser import HTMLParser
from PyQt4.QtGui import QApplication


class MyHTMLParser(HTMLParser):
    result = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if 'data-file' in attr[0]:
                    self.result.append(attr[1])


class AmericanSays:
    BASE_URL = 'http://www.merriam-webster.com/dictionary/'
    MP3_URL = 'http://media.merriam-webster.com/audio/prons/en/us/mp3/%s/%s.mp3'

    def get_selected(self, view):
        """Copy selected text. only the first word will be chosen"""
        return view.page().selectedText().encode('utf8', 'ignore').split()[0]

    def lookup_character_action(self, view):
        """Lookup single character action"""
        selected = self.get_selected(view)
        content = urllib2.urlopen(
            self.BASE_URL + selected).read()
        parser = MyHTMLParser()
        parser.feed(content)
        filename = None
        for i in parser.result:
            # may have multiple prounce files, but only choose first matched
            if i[:6] == selected[:6]:
                filename = i
                break

        # copy link to clipboard
        if filename:
            clipboard = QApplication.clipboard()
            clipboard.clear(mode=clipboard.Clipboard)
            clipboard.setText(self.MP3_URL % (filename[0], filename),
                              mode=clipboard.Clipboard)
        else:
            showInfo('No prounce file founded.')

    def insert_search_menu_action(self, anki_web_view, m):
        selected = self.get_selected(anki_web_view)
        a = m.addAction('American Says')
        a.connect(a, SIGNAL("triggered()"),
                  lambda wv=anki_web_view: self.lookup_character_action(wv))

# only insert into content menu in editor window
says = AmericanSays()
addHook("EditorWebView.contextMenuEvent", says.insert_search_menu_action)
