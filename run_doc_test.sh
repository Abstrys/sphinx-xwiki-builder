#!/bin/sh
./setup.py install --user
cd test_docs
sphinx-build -b xwiki source build
xclip -selection clipboard build/xwiki/TestPage.xwiki
cd ..
