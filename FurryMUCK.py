#!/usr/bin/env python3
import sys
import ssl
import asyncio
import websockets
import daemon
print ( 'FurryMUCK TCP-WebSocket Relay Server. 2019 Arctic Kona. No rights reserved. http://arcticjieer.fam.cx/ mailto:arcticjieer@gmail.com' )

muck_host = 'furrymuck.com'
muck_port = 8899
muck_ssl = ssl.create_default_context ( cafile = 'FurryMUCK.pem' )
server_host = '0.0.0.0'
server_port = '2001'
#server_ssl = ssl.SSLContext ( )
#server_ssl.load_cert_chain ( certfile = 'ssl_cert.pem' , keyfile = 'ssl_key.pem' )
server_daemon = True

if len( sys.argv ) > 1:
	server_port = sys.argv[1]
if len( sys.argv ) > 2:
	server_host = sys.argv[2]

def start_server ( ):
	async def tomuck ( websocket , socketwrite ):
		while True:
			try:
				msg = await websocket.recv( )
			except:
				break
			socketwrite.write ( msg.encode( 'UTF-8' ) )
		# close connection when websocket dies
		socketwrite.close( )
		await socketwrite.wait_close( )

	async def frommuck ( websocket , socketread ):
		while ( not socketread.at_eof ( ) ):
			msg = await socketread.read( 4096 )
			await websocket.send( msg.decode( 'UTF-8' ) )
		# when TCP dies
		websocket.send ( 'connection close' )

	async def muck ( websocket , path ):
		socketread , socketwrite = await asyncio.open_connection ( muck_host , muck_port , ssl = muck_ssl )
		# Prepare tasks
		tomuck_task = asyncio.ensure_future( tomuck ( websocket , socketwrite ) )
		frommuck_task = asyncio.ensure_future( frommuck ( websocket , socketread ) )
		await tomuck_task
		await frommuck_task
		
	asyncio.get_event_loop( ).run_until_complete( websockets.serve ( muck , server_host , server_port ) )
	asyncio.get_event_loop( ).run_forever( )

# launch daemon
if server_daemon:
	with daemon.DaemonContext ( ):
		start_server ( )
else:
	start_server ( )


