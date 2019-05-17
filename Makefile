all:
	rm -f dist/*
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

install:
	(cd ~ && python3 -m pip install --upgrade pywup)

