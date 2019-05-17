all:
	rm -f dist/*
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

install:
	(cd ~ && sudo python3 -m pip install --upgrade pywup)

uninstall:
	sudo pip uninstall pywup -y

localinstall: uninstall all
	sudo pip install ./dist/pywup-*-py3-none-any.whl

