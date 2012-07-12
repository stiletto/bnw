# TODO: Update and refactor it.
# Зависимости составлялись для попсоубунты 10.10.
# Тут, к примеру из коробки есть python-twisted-core

DEPS=	python-pyrss2gen\
	ejabberd\
	python-twisted-words\
	mongodb-server

run:
	twistd -ny instance.tac

install: config.py tornado txWebSocket mongo-async-python-driver

config.py:
	cp config.py.example config.py
	/usr/bin/editor config.py

tornado:
	git clone https://github.com/dustin/tornado.git tornado

mongo-async-python-driver:
	git clone https://github.com/fiorix/mongo-async-python-driver.git mongo-async-python-driver

txWebSocket:
	git clone https://github.com/rlotun/txWebSocket.git txWebSocket

install-deb:
	sudo aptitude install $(DEPS)

uninstall-deb:
	sudo aptitude remove $(DEPS)
