
import os

for root, dirs, files in os.walk(os.path.abspath(os.path.dirname(__file__))):
    for file in files:
        name, ext = os.path.splitext(file)
        if ext == '.pyc':
            os.unlink(os.path.join(root, file))