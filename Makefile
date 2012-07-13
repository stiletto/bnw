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

PIP=.venv/bin/pip

install-venv:
	sudo apt-get install $(VENV_DEPS)
	virtualenv .venv
	$(PIP) install twisted tornado PyRSS2Gen
	$(PIP) install -e git+https://github.com/fiorix/mongo-async-python-driver.git#egg=txmongo
	git clone https://github.com/stiletto/linkshit.git

uninstall-venv:
	rm -rfv .venv linkshit
	sudo apt-get autoremove $(VENV_DEPS)

rm-venv:
	rm -rfv .venv

reinstall-venv: rm-venv install-venv

config:
	cp -i config.py.example config.py
	test $(EDITOR) && $(EDITOR) config.py || editor config.py

RUN_CMD=twistd -ny instance.tac

run:
	test -d .venv &&\
		bash -c "source .venv/bin/activate; $(RUN_CMD)" ||\
		$(RUN_CMD)
