import json
import socket
import threading
import time
import uuid
from typing import Optional

HOST = "127.0.0.1"  # Change this to your desired IP
PORT = 8766       # Change this to your desired port (different from receiver)
INPUT_FILE = "socket_temp/robot_response.json"


class SocketSender:
	"""Socket client that watches a file and sends updates to connected clients"""
	
	def __init__(self, host: str = HOST, port: int = PORT, input_file: str = INPUT_FILE):
		self.host = host
		self.port = port
		self.input_file = input_file
		self.is_running = False
		self.last_content = None
		self.client_socket: Optional[socket.socket] = None
		self.connected = False
	
	def _connect(self):
		"""Establish connection to the server"""
		try:
			self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client_socket.settimeout(5.0)  # Set timeout for recv operations
			self.client_socket.connect((self.host, self.port))
			self.connected = True
			print(f"Connected to server at {self.host}:{self.port}")
		except Exception as e:
			print(f"Connection failed: {e}")
			self.connected = False
			if self.client_socket:
				try:
					self.client_socket.close()
				except:
					pass
			self.client_socket = None
	
	def _reconnect(self):
		"""Attempt to reconnect to the server"""
		self._close_connection()
		time.sleep(1)  # Wait before reconnecting
		self._connect()
	
	def _send_data(self, data: dict):
		"""Send data to the connected server"""
		if not self.connected or not self.client_socket:
			print("Not connected, skipping send")
			return False
		
		try:
			# Ensure unique ID for each message (required for frontend de-duplication)
			if "id" not in data or not data["id"]:
				data = dict(data)  # Make a copy to avoid modifying original
				data["id"] = str(uuid.uuid4())
			
			message = json.dumps(data, ensure_ascii=False)
			print(f"About to send to socket: {message}")
			self.client_socket.sendall((message + "\n").encode("utf-8"))
			
			# Wait for ACK response (OK\n or ERR:...\n)
			ack = self._recv_line()
			print(f"Sent: {message}")
			print(f"ACK: {ack}")
			
			# Close connection after each message (clean disconnect)
			self._close_connection()
			
			if ack and ack.startswith("OK"):
				return True
			else:
				print(f"Unexpected ACK: {ack}")
				return False
		except Exception as e:
			print(f"Send error: {e}")
			self.connected = False
			return False
	
	def _close_connection(self):
		"""Close the current connection cleanly"""
		if self.client_socket:
			try:
				self.client_socket.close()
			except:
				pass
		self.client_socket = None
		self.connected = False
	
	def _recv_line(self):
		"""Receive a line from the server"""
		try:
			data = b""
			while not data.endswith(b"\n"):
				chunk = self.client_socket.recv(4096)
				if not chunk:
					print("Server closed connection")
					self.connected = False
					return None
				data += chunk
				if len(data) > 65536:  # Safety limit
					print("Response too large")
					return None
			return data.decode("utf-8", errors="replace").strip()
		except socket.timeout:
			print("Timeout waiting for ACK")
			self.connected = False
			return None
		except Exception as e:
			print(f"Recv error: {e}")
			self.connected = False
			return None
	
	def start(self):
		"""Start the file watcher and sender"""
		self.is_running = True
		
		# Start connection in a separate thread
		def connection_loop():
			while self.is_running:
				if not self.connected:
					self._connect()
				time.sleep(1)
		
		connection_thread = threading.Thread(target=connection_loop, daemon=True)
		connection_thread.start()
		
		# Main file watching loop
		print(f"Watching {self.input_file} for changes...")
		
		while self.is_running:
			try:
				# Check if file exists and read it
				try:
					with open(self.input_file, "r") as f:
						content = f.read()
						current_content = json.loads(content)
				except FileNotFoundError:
					time.sleep(0.5)
					continue
				except json.JSONDecodeError:
					time.sleep(0.5)
					continue
				
				# Check if content has changed
				if current_content != self.last_content:
					print(f"File update detected: {current_content}")
					
					# Send the data
					if self.connected:
						print(f"Connection status: connected={self.connected}, socket={'open' if self.client_socket else 'closed'}")
						if self._send_data(current_content):
							# Only update last_content if send was successful
							self.last_content = current_content
							print("✓ Send successful, marked as sent")
						else:
							print("✗ Send failed, will retry after reconnect")
							self._reconnect()
					else:
						print("Not connected, waiting for connection...")
				
				time.sleep(0.5)  # Check file every 500ms
				
			except Exception as e:
				if self.is_running:
					print(f"Error in file watcher: {e}")
					time.sleep(1)
	
	def stop(self):
		"""Stop the sender"""
		self.is_running = False
		self._close_connection()
		print("Socket sender stopped")


if __name__ == "__main__":
	# Standalone mode - connect to a test server
	sender = SocketSender()
	try:
		sender.start()
	except KeyboardInterrupt:
		sender.stop()
		print("\nSocket sender stopped")


