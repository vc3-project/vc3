#!/usr/bin/env python

from service import app

if __name__ == '__main__':
    app.run(host='localhost', ssl_context=('./ssl/server.crt', './ssl/server.key'))
