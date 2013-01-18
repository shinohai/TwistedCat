from twisted.words.protocols import irc
from twisted.internet import protocol, ssl
import platform, socket, getpass

class IRCBot(irc.IRCClient):
    
    usage_message = None

    def _get_nickname(self):
        return self.factory.config['nick']
    nickname = property(_get_nickname)

    def _get_username(self):
        return self.factory.config['user']
    username = property(_get_username)

    def _get_realname(self):
        return self.factory.config['realname']
    realname = property(_get_realname)

    def _get_password(self):
        return self.factory.config['pass']
    password = property(_get_password)

    def _get_lineRate(self):
        return self.factory.config['lineRate']
    lineRate = property(_get_lineRate)

    versionName = "TwistedCat"

    def signedOn(self):
    	for channel in self.factory.config['channels']:
		if self.factory.config['channels'][channel] and self.factory.config['channels'][channel].has_key('key'):
        		self.join(channel, self.factory.config['channels'][channel]['key'])
		else:
        		self.join(channel)

        print "Signed on as %s." % (self.nickname,)
	self.factory.irc = self

    def joined(self, channel):
        print "Joined %s." % (channel,)

    """This will get called when the bot receives a message."""
    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        print "<%s> %s" % (user, msg)
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg = "%s: I am a log bot" % user
            self.msg(channel, msg)
            print "<%s> %s" % (self.nickname, msg)
        elif msg.startswith(self.nickname + "?"):
            msg = self.factory.usage_msg
            self.msg(channel, msg)
            print "<%s> %s" % (self.nickname, msg)


class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot
    usage_msg = None

    def __init__(self, config, appinfo):
        self.appinfo = appinfo
        global APP_VERSION
        self.config = config
        hostname = socket.gethostbyname(platform.uname()[1])
        username = getpass.getuser()
        self.usage_msg = "%s\nrunning on %s as %s" % (appinfo, hostname, username)

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

    def msg(self, message):
	for dest in self.config['channels']:
       		self.irc.msg(dest, message)
        if self.config['users'] is not None:
            for dest in self.config['users']:
       		self.irc.msg(dest, message)
