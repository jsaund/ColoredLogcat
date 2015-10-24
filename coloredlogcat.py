#!/usr/bin/python

'''
    Copyright 2015, Jag Saund

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

# Color coded logcat script to highlight adb logcat output for console.

import cStringIO
import fcntl
import os
import re
import struct
import sys
import termios

# pattern to extract data from log
# the pattern currently conforms to the log output received from
# adb 1.0.31
PATTERN = "^(\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}\.\d{3}) ([VDIWE])\/(.*)(\(\s+\d+\)):(.*)$"

# formatting properties
LOG_LEVEL_VERBOSE = '\033[38;5;225;48;5;8m'
LOG_LEVEL_INFO = '\033[0;30;48;5;119m'
LOG_LEVEL_DEBUG = '\033[0;30;48;5;45m'
LOG_LEVEL_WARNING = '\033[0;30;48;5;229m'
LOG_LEVEL_ERROR = '\033[38;5;225;48;5;196m'
LOG_PROCESS = '\033[0;38;5;244;48;5;236m'
LOG_TAG = '\033[0;38;5;%dm'
LOG_TIMESTAMP = '\033[0;38;5;235m'
RESET = '\033[0m'

# column widths
WIDTH_LOG_LEVEL = 3
WIDTH_TAG = 25
WIDTH_PID = 7
WIDTH_TIMESTAMP = 12
HEADER_SIZE = WIDTH_TIMESTAMP + 1 + WIDTH_PID + 1 + WIDTH_TAG + 1 + WIDTH_LOG_LEVEL + 1

# log level formatting
LOG_LEVEL_FORMATTING = {
    'V': LOG_LEVEL_VERBOSE,
    'I': LOG_LEVEL_INFO,
    'D': LOG_LEVEL_DEBUG,
    'W': LOG_LEVEL_WARNING,
    'E': LOG_LEVEL_ERROR
}

# tag colors
TAG_COLORS = [ 226, 220, 213, 203, 199, 195, 190, 160, 105, 87, 75, 39, 13, 11, 10 ]

# color cache
tag_color_cache = dict()
color_index = 0

def format(text, width, format_prop=None, align='left'):
    if align == 'center':
        text = text.center(width)
    elif align == 'right':
        text = text.rjust(width)
    if format_prop:
        text = format_prop + text + RESET
    return text

def get_color(tag):
    color = tag_color_cache.get(tag)
    if not color:
        global color_index
        color = LOG_TAG % TAG_COLORS[color_index]
        color_index = (color_index + 1) % len(TAG_COLORS)
        tag_color_cache[tag] = color
    return color

def wrap_text(text, buf, indent=0, width=80):
    text_length = len(text)
    wrap_length = width - indent
    pos = 0
    while pos < text_length:
        next = min(pos + wrap_length, text_length)
        buf.write(text[pos:next])
        if next < text_length:
            buf.write("\n%s" % (" " * indent))
        pos = next
    wraped_text = buf.getvalue()

def extractPID(package):
    # attempt to extract the process ID from adb shell
    # if there is no pid associated with the package name then return None
    input = os.popen("adb shell ps | grep %s" % package)
    try:
        line = input.readline()
    except:
        return None
    else:
        if not line:
            return None
        return line.split()[1]
    finally:
        input.close()

def main():
    # unpack the current terminal width/height
    data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
    height, width = struct.unpack('hh', data)

    retag = re.compile(PATTERN)
    pid = None
    if len(sys.argv) > 1:
        package = sys.argv[1]
        pid = extractPID(package)

    proc = None

    # if someone is piping in to us, use stdin as input.  if not, invoke adb logcat
    if os.isatty(sys.stdin.fileno()):
        cmd = "adb logcat -v time"
        pipe = os.popen(cmd)
    else:
        pipe = sys.stdin

    while True:
        try:
            line = pipe.readline()
        except KeyboardInterrupt:
            break
        except Exception, err:
            print err
            break
        else:
            match = retag.match(line)
            if match:
                date, timestamp, tagtype, tag, procID, message = match.groups()
                procID = procID[1:-1]
                if pid and procID != pid:
                    continue

                linebuf = cStringIO.StringIO()
                linebuf.write(format(timestamp, WIDTH_TIMESTAMP, LOG_TIMESTAMP, 'center') + " ")
                linebuf.write(format(procID, WIDTH_PID, LOG_PROCESS, 'center') + " ")
                linebuf.write(format(tag.strip()[-WIDTH_TAG:], WIDTH_TAG, get_color(tag), 'right') + " ")
                linebuf.write(format(tagtype, WIDTH_LOG_LEVEL, LOG_LEVEL_FORMATTING[tagtype], 'center') + " ")
                wrap_text(message, linebuf, HEADER_SIZE + 1, width)

                print linebuf.getvalue()
                linebuf.close()
        finally:
            if proc:
                proc.terminate()


if __name__ == "__main__":
    main()

