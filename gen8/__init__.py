# gen8 - A web based fortune teller
# Copyright 2019 Brian 'redbeard' Harrington, Ace Monster Toys
#
# This file is part of gen8
#
# gen8 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gen8 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with gen8.  If not, see <https://www.gnu.org/licenses/>.

import sys
import time

from random import randint
from flask import Flask, Response, render_template

# NOTE: the use of a global variable in this way is not thread safe
# This works because it's a PoC to be used on a single system and really the
# purpose is just to keep there from the same message being served back to back
# so safety on the process isn't critical
msg = "All will become clear in time."

# define and build the application
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # boilerplate for _potentially_ using a config file at some later date
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Load our messages from the file messages.txt
    try:
        with app.open_resource("messages.txt", "r") as f:
            messages = f.readlines()
        messages = [x.strip() for x in messages]
        print("Populated messages with {} messages".format(len(messages)))
    except FileNotFoundError:
        print("You need to create a file named messages.txt")
        sys.exit(1)


    # Base application path, show the fortune on the screen
    @app.route('/')
    def show_message(msg=None):
        return render_template('message.html', msg=msg)

    # endpoint which will generate a new message
    @app.route('/newmsg')
    def get_message():
        global msg
        newmsg = msg
        while True:
            index = randint(0, len(messages)-1)
            msg = messages[index]
            if newmsg != msg: break
        print("  Printing message number {}, {}".format(index, msg))
        return Response("changing message")

    # function to return the current message to the stream
    def print_message():
        return msg

    # stream for generating server sent events to avoid the need for webhooks
    # or a full caching system
    @app.route('/stream')
    def stream():
        def event_stream():
            while True:
                time.sleep(0.10)
                yield 'data: {}\n\n'.format(print_message())
        return Response(event_stream(), mimetype="text/event-stream")

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    return app
