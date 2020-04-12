import os
import sys

if getattr(sys, "frozen", False):
    # we are running in a bundle
    PROD = True
    # bundle_dir = sys._MEIPASS
else:
    PROD = False
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
