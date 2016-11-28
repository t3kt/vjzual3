print('shell/server.py initializing')

# based on https://www.derivative.ca/Forum/viewtopic.php?p=30301

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base as base
try:
	import common_util as util
except ImportError:
	try:
		import util
	except ImportError:
		import common.lib.util as util

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

import hashlib
import base64
import json
import struct
import array
import os.path
import mimetypes

class WebsocketServer(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.Initialize()

	def Initialize(self):
		self._LogEvent('Initialize()')
		self._Peers = {}

	@property
	def _Peers(self):
		return self.comp.fetch('peerList', {}, search=False, storeDefault=True)

	@_Peers.setter
	def _Peers(self, peerlist):
		self.comp.store('peerList', peerlist)

	@property
	def _ClosePeerScript(self):
		return self.comp.op('./close_peer')

	def _ClosePeerNextFrame(self, peer):
		self._ClosePeerScript.run(peer, delayFrames=1)

	def _RemovePeer(self, peer):
		peers = self._Peers
		if peer.port in peers:
			del peers[peer.port]
		self._Peers = peers

	def _AddPeer(self, peer):
		peers = self._Peers
		peers[peer.port] = peer
		self._Peers = peers

	def HandleRequest(self, message, msgbytes, peer):
		self._LogEvent('HandleRequest(peer: %r' % peer)
		if message.startswith('GET '):
			self._HandleWebRequest(msgbytes, peer)
		else:
			self._HandleMessageRequest(msgbytes, peer)

	def _HandleWebRequest(self, msgbytes, peer):
		fullMsg = msgbytes.decode('utf-8')
		msgList = fullMsg.splitlines()
		path = msgList[0].split(' ')[1]
		headers = {
			'GET': path
		}
		for line in msgList[1:]:
			keyval = line.split(': ')
			if len(keyval) == 2:
				headers[keyval[0]] = keyval[1]
		if path == '/connect':
			self._AddPeer(peer)
			sendHeader = self._GetHeader(hType='websocket', recHeader=headers)
			sendHello = json.dumps({'type': 'system', 'message': 'Hello from %s!' % app.product})
			packedMsg = _Encode(sendHello.encode('utf-8'))
			packedMsg = b''.join(packedMsg)
			peer.sendBytes(sendHeader)
			peer.sendBytes(packedMsg)
		else:
			# TODO: deal with this better?
			self._ServeWebFile(path, peer, headers)
			# raise Exception('Unsupported path: %r' % path)
			# sendHeader = self._GetHeader(hType='404')
			# peer.sendBytes(sendHeader)
			# #peer.close()

	@property
	def _WebRootDir(self):
		return self.comp.par.Webfolder.eval() or self.comp.par.Webfolder.default

	def _ServeWebFile(self, path, peer, headers):
		if path == '/':
			path = '/index.html'
		if path.startswith('/'):
			path = path[1:]
		if '..' in path:
			raise Exception('Invalid path')
		rootdir = self._WebRootDir
		fullpath = os.path.join(rootdir, path)
		self._LogEvent('_ServeWebFile(path: %r) - fullpath: %r' % (path, fullpath))
		if not os.path.isfile(fullpath):
			peer.sendBytes(self._GetHeader(hType='404'))
			return
		mtype = mimetypes.guess_type(path)
		self._LogEvent('_ServeWebFile(path: %r) - mimetype: %r' % (path, mtype))
		try:
			if mtype[0].startswith('text/'):
				with open(fullpath, 'rt') as f:
					data = f.read()
				if '[[PORT]]' in data:
					data = data.replace('[[PORT]]', str(self.comp.par.Port.eval()))
			else:
				with open(fullpath, 'rb') as f:
					data = f.read()
			sendHeader = self._GetHeader(hType='default', recHeader=headers, contentType=mtype[0])
			peer.sendBytes(sendHeader)
			peer.sendBytes(data)
			self._ClosePeerNextFrame(peer)
		except Exception as e:
			# TODO: error handling
			raise e
		pass

	def _HandleMessageRequest(self, msgbytes, peer):
		fullMsg = _UnpackFrame(msgbytes)
		if fullMsg['payload'] == b'\x03\xe9':
			self._RemovePeer(peer)
			peer.close()
			return
		try:
			self._LogEvent('_HandleMessageRequest() payload: %r' % fullMsg['payload'])
			rawpayload = fullMsg['payload']
			if isinstance(rawpayload, bytes):
				rawpayload = rawpayload.decode('utf-8')
			payload = json.loads(rawpayload)
			msgType = payload.get('type', None)
			self._HandleMessage(msgType, payload)
		except Exception as e:
			peer.close()
			self._RemovePeer(peer)
			raise Exception('Error handling request: %r' % e)

	def _HandleMessage(self, msgType, payload):
		value = payload.get('value', 0)
		if msgType == 'slider':
			self.comp.op('./fromWeb').par.value0 = value
		elif msgType == 'slider1':
			self.comp.op('./fromWeb').par.value1 = value
		else:
			returnMsg = json.dumps({'type': 'usermsg', 'message': payload['message'], 'name': payload['name']})
			packedMsg = _Encode(returnMsg.encode('utf-8'))
			packedMsg = b''.join(packedMsg)
			for peer in self._Peers.values():
				peer.sendBytes(packedMsg)

	def SendMessage(self, message):
		returnMsg = json.dumps({'type': 'system', 'message': message})
		packedMsg = _Encode(returnMsg.encode('utf-8'))
		packedMsg = b''.join(packedMsg)
		for peer in self._Peers.values():
			peer.sendBytes(packedMsg)

	def _GetHeader(self, hType=None, recHeader=None, contentType=None):
		if hType == 'default':
			# TODO: deal with charsets for binary stuff
			return ('HTTP/1.x 200 OK\n\rContent-Type: %s; charset=UTF-8\n\r\n\r' % (contentType or 'text/html')).encode('ascii')
		elif hType == 'websocket':
			SecKey = recHeader.get('Sec-WebSocket-Key', None)
			# TODO: figure out what to do if there isn't a sec key
			if not SecKey:
				self._LogEvent('_GetHeader() - no sec key. recHeader: %r' % recHeader)
				raise Exception('_GetHeader(): no sec key!')
			h = hashlib.sha1()
			h.update(str.encode(SecKey+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'))
			responseKey = base64.b64encode(h.digest())
			return b'HTTP/1.1 101 Web Socket Protocol Handshake\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nWebSocket-Origin: localhost\r\nWebSocket-Location: localhost:7000/demo/shout\r\nSec-WebSocket-Accept:'+responseKey+b'\r\n\r\n'
		elif hType == '404':
			return b'HTTP/1.x 404 File not found\n\r\n\r'
		else:
			raise Exception('_GetHeader() - unsupported hType: %r' % hType)


def _UnpackFrame(data):
	frame = {}
	byte1, byte2 = struct.unpack_from('!BB', data)
	frame['fin'] = (byte1 >> 7) & 1
	frame['opcode'] = byte1 & 0xf
	masked = (byte2 >> 7) & 1
	frame['masked'] = masked
	mask_offset = 4 if masked else 0
	payload_hint = byte2 & 0x7f
	if payload_hint < 126:
		payload_offset = 2
		payload_length = payload_hint
	elif payload_hint == 126:
		payload_offset = 4
		payload_length = struct.unpack_from('!H', data, 2)[0]
	elif payload_hint == 127:
		payload_offset = 8
		payload_length = struct.unpack_from('!Q', data, 2)[0]
	else:
		# TODO: is this actually an error?
		raise Exception('Unsupported payload hint: %r' % payload_hint)
	frame['length'] = payload_length
	payload = array.array('B')
	payload.fromstring(data[payload_offset + mask_offset:])
	if masked:
		mask_bytes = struct.unpack_from('!BBBB', data, payload_offset)
		for i in range(len(payload)):
			payload[i] ^= mask_bytes[i % 4]
	frame['payload'] = payload.tostring()
	return frame


def _Encode(bytesRaw):
	bytesFormatted = []
	bytesFormatted.append(struct.pack('B', 129))
	if len(bytesRaw) <= 125:
		bytesFormatted.append(struct.pack('B', len(bytesRaw)))
	elif 126 <= len(bytesRaw) <= 65535:
		bytesFormatted.append(struct.pack('B', 126))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw) >> 8) & 255))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw)) & 255))
	else:
		bytesFormatted.append(struct.pack('B', 127))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw) >> 56) & 255))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw) >> 48) & 255))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw) >> 40) & 255))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw) >> 32) & 255))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw) >> 24) & 255))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw) >> 16) & 255))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw) >> 8) & 255))
		bytesFormatted.append(struct.pack('B', (len(bytesRaw)) & 255))
	for i in range(len(bytesRaw)):
		# bytesFormatted.append(struct.pack('B', ord(bytesRaw[i])))
		bytesFormatted.append(struct.pack('B', bytesRaw[i]))
	return bytesFormatted

