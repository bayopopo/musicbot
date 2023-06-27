import os
import sys
from musicbot import MusicBot

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        os.environ['PATH'] += ';' + os.path.abspath('bin/')
        sys.path.append(os.path.abspath('bin/')) # might as well
    m = MusicBot()
    m.run()
  

