# Installing BnW

## Setting up MongoDB

The defaults are all right, but you might also want to do the following:

1. in `/etc/mongodb.conf`, set `bind_ip = 127.0.0.1` and `nohttpinterface
   = true`;

2. restart MongoDB:

        $ sudo service mongodb restart

   (for sysvinit, openrc and others), or

        $ sudo systemctl restart mongodb.service

   (for systemd);

3. drop some databases that were created by default:

        $ mongo test  --eval 'db.dropDatabase()'
        $ mongo local --eval 'db.dropDatabase()'

## Setting up Prosody

BnW does require an XMPP server, but not Prosody specifically - any one that
supports [XEP-0114: Jabber Component
Protocol](http://xmpp.org/extensions/xep-0114.html) will do. We do recommend
Prosody, though, as it's easy to install and configure.

There are two possible setups: a local one, suitable for developing things
locally, and a public one, intended for those who want to host their own
instance.

### Local setup

1. In the global section (i.e. before the line saying "----------- Virtual hosts
   -----------") of `/etc/prosody/prosody.cfg.lua` set the following:

        c2s_interface = "127.0.0.1"
        s2s_interface = "127.0.0.1"
        legacy_ssl_interface = "127.0.0.1"

2. edit local virtual host's config,
   `/etc/prosody/conf.avail/localhost.cfg.lua`, appending these lines at the end
   of it:

        Component "bnw.localhost"
          component_secret = "here goes your component's authorization password"

   (You can use anything in place of "bnw", it's only ".localhost" postfix that
   is required);

3. restart Prosody:
    
        $ sudo service prosody restart

### Public setup

Assuming that the server you're hosting BnW on has a domain name `example.com`,
and you want BnW to be available at `bnw.example.com`:

1. create a file named `/etc/prosody/conf.avail/example.com.cfg.lua` and put the
   following lines in there:

        VirtualHost "example.com"

        Component "bnw.example.com"
          component_secret = "here goes your component's authorization password"

   Or vice versa: the service is at `example.com`, but XMPP server is at
   `xmpp.example.com`:

        VirtualHost "xmpp.example.com"

        Component "example.com"
          component_secret = "here goes your component's authorization password"

2. activate the config you've just created and deactivate the default local one:

        $ sudo ln -s /etc/prosody/conf.avail/example.com.cfg.lua \
                   /etc/prosody/conf.d/example.com.cfg.lua
        $ sudo unlink /etc/prosody/conf.d/localhost.cfg.lua

3. restart Prosody:
    
        $ sudo service prosody restart

Registration using a client is disabled by default, but you can create an
account from the command line:

    $ sudo prosodyctl adduser user@localhost

(substitute "localhost" with the name of your public service if you've set it up
that way). When using public setup, you can also use an account on any other
XMPP server.

## Setting up an HTTP server

### Local setup

BnW starts a web interface at [localhost:7808](http://localhost:7808) by
default. No further configuration is required.

### Public setup

We advise **not** to expose default HTTP interface to the Internet. Set up an
Nginx proxy or something.

## Final steps

1. In the directory with the BnW source code, run the following:

        $ virtualenv --system-site-packages .venv

   This will create a directory called `.venv` containing Python virtual environment;

2. copy the default config:

        $ cp config.py.example config.py

   and adjust `srvc_pwd` to match the password you've set for your component in
   Prosody's config;

3. deploy BnW:

        $ .venv/bin/python setup.py install

   When run for the first time, this command will download and install all the
   dependencies. Afterwards, it will only re-deploy the project into virtual
   environment.

   Note that **you need to re-run this command every time you change the source
   code**;

4. at long last, start BnW:

        $ PYTHONPATH=. .venv/bin/bnw -n

   (we need to set `PYTHONPATH` to current directory, i.e. `.`, so that it picks
   up the configuration file).

You should now be able to see BnW's default home page at
[localhost:7808](http://localhost:7808).
