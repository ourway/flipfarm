
# -*- coding: utf-8 -*-

__author__ = 'Farsheed Ashouri'

"""
   ___              _                   _
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an apology!
Clean code is much better than Cleaner comments!
'''


'''
@desc: utils/parsers/alfred.py
@author: F.Ashouri
"""

import re

def parse(alfredJob):
    '''Regex parser
        based on: http://regexr.com/3bg9a
    '''
    #pat = r'Task \-title \{Render ([\w ]+)\} [\w \- \{ \n : %]+"%D\(([\w:/\-]+)\)"[ ]+"%D\(([\w\d . /]+)\)"[\} \- \n \w \{:]+sho[ \n]+"([\w :\d/\.\-]+)"'
    pat = r'Task \-title \{(.*)}[\w \- \{ \n : % \.]*"%D\((.*)\)"[ ]*"%D\((.*)\)"\} [\n \- \w\d\{:\}]*sho [\n]*"(.*)"'
    data = re.findall(re.compile(pat), alfredJob)
    result = {'tasks': [{
                            'name':i[0],
                            'cwd':i[1],
                            'filepath':i[2], ## command will act upon this file
                            'target':i[3]  ## command will produce this file
                        } for i in data]
            }
    return result
