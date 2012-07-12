# TODO: Update and refactor it.
# Зависимости составлялись для попсоубунты 10.10.
# Тут, к примеру из коробки есть python-twisted-core

DEPS=	python-pyrss2gen\
	ejabberd\
	python-twisted-words\
	mongodb-server

run:
	twistd -ny instance.tac

install: config.py tornado mongo-async-python-driver

config.py:
	cp -i config.py.example config.py
	/usr/bin/editor config.py

tornado:
	git clone https://github.com/dustin/tornado.git

mongo-async-python-driver:
	git clone https://github.com/fiorix/mongo-async-python-driver.git

install-deb:
	sudo apt-get install $(DEPS)

uninstall-deb:
	sudo apt-get autoremove $(DEPS)
