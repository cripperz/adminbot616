#Adminbot

This is a simple IRC bot which  can do some basic server *nix managing

It can adduser, delete them, mail them etc.

If you want to find me get me on [#adminbot][1] on freenode
If you want to discuss about the bot, join [#adminbot-dev][2] on freenode

#Running the bot


You need Python 2.7 to run the bot

copy `config.py.example` to `config.py` and make necessary changes.

to run the bot, type `./bot.py` you can use `-v` or `--verbose` to see all IRC messages and `-c` or `--control` to send raw IRC commands from stdin aka the program itself 
[1]: https://kiwiirc.com/client/chat.freenode.net:+6697/#adminbot
[2]: https://kiwiirc.com/client/chat.freenode.net:+6697/#adminbot-dev