DEBIAN_DEPS=\
	python-twisted\
	python-tornado\
	python-pyrss2gen\
	python-pip\
	build-essential\
	python-dev\
	mongodb-server

VENV_DEPS=\
	python-virtualenv\
	build-essential\
	python-dev\
	mongodb-server

install-deb:
	sudo apt-get install $(DEBIAN_DEPS)
	sudo pip install git+https://github.com/fiorix/mongo-async-python-driver.git#egg=txmongo
	git clone https://github.com/stiletto/linkshit.git

uninstall-deb:
	sudo pip uninstall txmongo
	rm -rfv linkshit
	sudo apt-get autoremove $(DEBIAN_DEPS)

install-venv:
	sudo apt-get install $(VENV_DEPS)
	virtualenv .venv
	source .venv/bin/activate
	pip install twisted tornado PyRSS2Gen
	pip install -e git+https://github.com/fiorix/mongo-async-python-driver.git#egg=txmongo
	git clone https://github.com/stiletto/linkshit.git

uninstall-venv:
	deactivate
	rm -rfv .venv
	sudo apt-get autoremove $(VENV_DEPS)

config:
	cp -i config.py.example config.py
	$(EDITOR) config.py

run:
	twistd -ny instance.tac
