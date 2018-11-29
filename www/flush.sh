#!/bin/bash

rm -rf __pycache__

rm -rf static/blogs/*/*/*.html

python3 markdownparser.py