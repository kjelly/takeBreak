#! /usr/bin/python
import os
import os.path
from lib import get_base_path


os.system("python " + get_base_path() + "/takeBreak.py & disown")
