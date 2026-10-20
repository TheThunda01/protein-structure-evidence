.PHONY: demo test
demo:
	python analyze.py
test:
	python -m unittest discover -s tests -v
