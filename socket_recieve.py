import json
import socket
from typing import Callable, Optional

HOST = "127.0.0.1"  # Change this to your desired IP
PORT = 8765       # Change this to your desired port
OUTPUT_FILE = "socket_temp/robot_receive.json"


class SocketReceiver:
	"""Socket server that receives text and triggers processing callback"""
	
	def __init__(self, host: str = HOST, port: int = PORT, output_file: str = OUTPUT_FILE):
		self.host = host
		self.port = port
		self.output_file = output_file
		self.callback: Optional[Callable[[str], None]] = None
		self.server = None
		self.is_running = False
	
	def set_callback(self, callback: Callable[[str], None]):
		"""Set callback function to be called when text is received"""
		self.callback = callback
	
	def start(self):
		"""Start the socket server"""
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((self.host, self.port))
		self.server.listen(1)
		self.is_running = True
		
		print(f"Socket listening on {self.host}:{self.port}")
		
		while self.is_running:
			try:
				conn, addr = self.server.accept()
				print(f"Connected: {addr}")
				
				data = conn.recv(1024).decode("utf-8").strip()
				
				if data:
					# If incoming data is JSON, write it as-is. Otherwise, wrap it.
					try:
						parsed = json.loads(data)
						payload = parsed
					except json.JSONDecodeError:
						payload = {
							"id": "1",
							"notaus": False,
							"text": data,
							"image_b64": ""
						}
					
					with open(self.output_file, "w") as f:
						json.dump(payload, f, indent=4)
					
					print(f"Received: {data}")
					conn.sendall(b"OK")
					
					# Trigger callback with the text (prefer 'text' if present)
					if self.callback:
						self.callback(payload["text"] if isinstance(payload, dict) and "text" in payload else data)
				
				conn.close()
			except Exception as e:
				if self.is_running:
					print(f"Error: {e}")
	
	def stop(self):
		"""Stop the socket server"""
		self.is_running = False
		if self.server:
			self.server.close()


if __name__ == "__main__":
	# Standalone mode
	receiver = SocketReceiver()
	try:
		receiver.start()
	except KeyboardInterrupt:
		receiver.stop()
		print("\nSocket receiver stopped")