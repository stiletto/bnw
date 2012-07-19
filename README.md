# BnW

BnW is XMPP microbblogging service written in Python. It's powered by  
Twisted, Tornado and MongoDB and aims to be scalable and high-performance.

## Installation

* Install necessary dependencies and python libraries from packages  
(for Debian):  
`% make install-deb`

* Alternatively, you can install BnW in virtualenv (for Debian):  
`% make install-venv`

* Create config file from stub and open it for editing:  
`% make config`

* Run BnW:  
`% make run`

Note that installation and configuration of XMPP and HTTP servers which will  
be used by BnW are still on your own. However you can find additional info  
by reading comments in config.py.example or looking at this page (in russian):  
http://hive.blasux.ru/u/Stiletto/BnW/Установка_BnW_на_Linux

## License

BnW licened under the following terms:
```
Copyright (c) 2010-2012, Stiletto <blasux@blasux.ru>
Copyright (c) 2012, Kagami Hiiragi <kagami@genshiken.org>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```
