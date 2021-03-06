from twisted.application import service, internet
from twisted.internet import reactor
import yaml

config = yaml.load(open('config.cfg', 'r'))

# Create the application
application = service.Application("ircnetcat")
factories = []

if config.has_key('irc'):
	# IRC Is enabled, so load the IRC Handler
	from irc import IRCBotFactory
	# Connect to IRC
	for server in config['irc']:
		f = IRCBotFactory(config['irc'][server])
		factories.append(f)
		if config['irc'][server]['ssl']:
			internet.SSLClient(config['irc'][server]['server'], config['irc'][server]['port'], f).setServiceParent(service.IServiceCollection(application))
		else:
			internet.TCPClient(config['irc'][server]['server'], config['irc'][server]['port'], f).setServiceParent(service.IServiceCollection(application))

if config.has_key('xmpp'):
	# XMPP Is enabled, so load the XMPP Handler
	from xmpp import XMPPBot
	from wokkel.client import XMPPClient
	from twisted.words.protocols.jabber import jid
	# Connect to IRC
	for user in config['xmpp']:
		client = XMPPClient(jid.internJID(user), config['xmpp'][user]['pass'])
		client.logTraffic = False
		bot = XMPPBot(config['xmpp'][user])
		bot.setHandlerParent(client)
		client.setServiceParent(application)
		factories.append(bot)

# This is the Netcat handler
from netcat import NetcatProtocol, NetcatFactory

# Listen for netcat connections
factory = NetcatFactory(factories=factories)
internet.TCPServer(config['netcat']['port'], factory).setServiceParent(service.IServiceCollection(application))
