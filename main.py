#!/usr/bin/env python3

import email.parser
from glob import glob
import os
from os.path import join
import py7zr  # pip install py7zr
from email.parser import Parser
from email.policy import default
import email.message
from typing import Literal, Tuple
import io
from collections import defaultdict
from datetime import datetime
from html import escape
import html
import html.parser
from html.parser import HTMLParser

# ...


def escape2(s: str):
    return "" if s == None else escape(s)


# ...


def GetBody(msg: email.message.EmailMessage) -> str:
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
    simplest = msg.get_body(preferencelist=('plain', 'html'))
    content = simplest.get_content()
    return content

# ...


class EmailHandler:
    def __init__(self):
        pass

    def ProcessFile(self, key: str, fileBytes: bytes, archive: str):
        '''
        key - value like 'tmp/000001' representing filename of file in archive.
        archive - name of zip/7z file like 'retr-17-09-11_21-54-16.zip.7z'
        fileBytes - the eml file.
        '''
        decoded = None
        for decodeType in ["cp1252", "ascii", "utf-8"]:
            try:
                decoded = fileBytes.decode(decodeType)
                break
            except Exception as e:
                pass

        if decoded == None:
            return

        headers = Parser(policy=default).parsestr(decoded)
        if type(headers) == email.message.EmailMessage:
            body = GetBody(headers)
            yield headers['Date']
            yield f"<p>Subject: {escape2(headers['Subject'])}</p>"
            yield f"<p>From: {escape2(headers['From'])}</p>"
            yield f"<p>To: {escape2(headers['To'])}</p>"
            yield f"<p>Date: {escape2(headers['Date'])}</p>"
            yield "<p></p>"
            if "<html" in body:
                class MyHTMLParser(HTMLParser):
                    _body: bool
                    _collector: str

                    def __init__(self):
                        super().__init__()
                        self._body = False
                        self._collector = ""

                    def handle_starttag(self, tag, attrs):
                        if tag == 'body':
                            self._body = True
                        elif self._body == True:
                            self._collector += f"<{tag}>"
                        pass

                    def handle_endtag(self, tag):
                        if tag == 'body':
                            self._body = False
                        elif self._body == True:
                            self._collector += f"</{tag}>"
                        pass

                    def handle_data(self, data):
                        if self._body == True:
                            self._collector += data

                parser = MyHTMLParser()
                parser.feed(body)
                yield parser._body
            else:
                yield "<div>"
                yield "<pre><code>"
                for line in body.splitlines(keepends=False):
                    for i in range(5):
                        if line.startswith("> "):
                            line = line[2:]
                        elif line.startswith(">"):
                            line = line[1:]
                        else:
                            break
                    yield escape2(line)
                yield "</code></pre>"
                yield "</div>"


def enumerateItems():
    rd = "src"
    for x in glob("*.7z", root_dir=rd):
        path = join(rd, x)
        with py7zr.SevenZipFile(path, mode='r') as z:
            items = z.readall()
            for key in items.keys():
                yield (key, items[key], path)


def main():
    HERE = os.path.dirname(os.path.realpath(__file__))
    os.chdir(HERE)
    emailHandler = EmailHandler()

    dd = defaultdict(list)
    with io.open("output.html", "w", encoding='utf-8') as fo:
        print(r"""<!DOCTYPE html>
<html lang="en">
  <head></head>
  <body>""", file=fo)
        for item in enumerateItems():
            key, iob, archive = item
            fb = iob.read()
            collector = None
            for line in emailHandler.ProcessFile(key, fb, archive):
                if collector == None:
                    # datetime.strptime("Fri, 09 Aug 2013 00:00:48 +0000")
                    dt: str = line
                    if line == None:
                        dt = datetime.fromtimestamp(0)
                        pass
                    else:
                        def bits():
                            for x in dt.split(","):
                                for y in x.split(" "):
                                    yield y
                        dt = [x for x in bits() if x != ''][1:5]
                        # dt = ['09', 'Aug', '2013', '00:00:48']
                        dt = datetime.strptime(
                            " ".join(dt), "%d %b %Y %H:%M:%S")
                    collector = dd[dt]
                    collector.append("")
                    collector.append(
                        f"<h1>{escape2(key)}, {escape2(archive)}</h1>")
                    collector.append("")
                    continue
                collector.append(line)
                pass
        for k in sorted(dd.keys()):
            stuff = dd[k]
            for line in stuff:
                print(line, file=fo)
                pass
            pass
        pass
        print(r"""</body>
</html>""", file=fo)


if __name__ == '__main__':
    main()
