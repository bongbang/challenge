#!/usr/bin/env bash
SRC=./src/venmo_degree.py
IN=./venmo_input/venmo-trans.txt
OUT=./venmo_output/output.txt

if hash python3 2>/dev/null; then
	python3 "$SRC" "$IN" "$OUT"
else
	echo ''
	echo 'No python3, trying python instead...'
	python "$SRC" "$IN" "$OUT"
fi
