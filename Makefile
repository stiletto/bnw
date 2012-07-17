DEBIAN_DEPS=\
	python-twisted\
	python-tornado\
	python-pyrss2gen\
	python-imaging\
	python-pip\
	build-essential\
	python-dev\
	mongodb-server

VENV_DEPS=\
	python-virtualenv\
	libjpeg-dev\
	zlib1g-dev\
	build-essential\
	python-dev\
	mongodb-server

install-deb:
	sudo apt-get install $(DEBIAN_DEPS)
	sudo pip install 'git+https://github.com/fiorix/mongo-async-python-driver.git#egg=txmongo'

uninstall-deb:
	sudo pip uninstall txmongo
	sudo apt-get autoremove $(DEBIAN_DEPS)

PIP=.venv/bin/pip

install-venv:
	sudo apt-get install $(VENV_DEPS)
	# http://jj.isgeek.net/2011/09/install-pil-with-jpeg-support-on-ubuntu-oneiric-64bits/
	# Why god, why?
	test -e /usr/lib/x86_64-linux-gnu/libjpeg.so && test ! -e /usr/lib/libjpeg.so &&\
		sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib
	test -e /usr/lib/x86_64-linux-gnu/libz.so && test ! -e /usr/lib/libz.so &&\
		sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib
	virtualenv .venv
	$(PIP) install twisted tornado PyRSS2Gen PIL
	$(PIP) install -e 'git+https://github.com/fiorix/mongo-async-python-driver.git#egg=txmongo'

uninstall-venv:
	rm -rfv .venv
	sudo apt-get autoremove $(VENV_DEPS)

rm-venv:
	rm -rfv .venv

reinstall-venv: rm-venv install-venv

config:
	cp -i config.py.example config.py
	if test $(EDITOR); then\
		$(EDITOR) config.py;\
	else\
		editor config.py;\
	fi

RUN_CMD=twistd -ny instance.tac
run:
	if test -d .venv; then\
		bash -c "source .venv/bin/activate && $(RUN_CMD)";\
	else\
		$(RUN_CMD);\
	fi

TEST_CMD=trial tests.test
test:
	if test -d .venv; then\
		bash -c "source .venv/bin/activate && $(TEST_CMD)";\
	else\
		$(TEST_CMD);\
	fi
