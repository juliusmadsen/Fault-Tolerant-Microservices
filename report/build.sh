#!/bin/bash
# Requires latexmk

cd tex
latexmk -pdf report.tex
latexmk -c # cleans temp files
