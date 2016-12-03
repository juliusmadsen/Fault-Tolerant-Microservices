#!/bin/bash
# Requires latexmk

cd tex
latexmk -pdf report
latexmk -c

