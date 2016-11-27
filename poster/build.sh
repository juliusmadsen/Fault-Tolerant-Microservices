#!/bin/bash
# Requires latexmk

latexmk -pdf poster.tex
latexmk -c # cleans temp files
