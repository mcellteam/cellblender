from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import mimetypes
import json
import sys
import webbrowser

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.path = '/plot-main.html'

		try:
			if self.path.endswith('.dat'):
				#change path if requesting series data
				self.path = os.path.relpath(sys.argv[1] + os.sep + self.path)

			self.send_response(200)
			mimetype, _ = mimetypes.guess_type(self.path)
			self.send_header('Content-type', mimetype)
			self.end_headers()
			
			f = open(os.curdir + os.sep + self.path, encoding="utf8")
			self.wfile.write(bytes(f.read(), "UTF-8"))
			f.close()
		except IOError:
			self.send_error(404, 'file not found')

	def do_POST(self):
		length = int(self.headers['Content-Length'])
		message = self.rfile.read(length).decode('utf-8')

		if self.path.endswith('server.py') and message == 'get_plot_specs':
			self.send_response(200)
			mimetype, _ = mimetypes.guess_type(self.path)
			self.send_header('Content-type', mimetype)
			self.end_headers()
			self.wfile.write(bytes(to_plot_spec(sys.argv[2:]), "UTF-8"))

def to_plot_spec(args):
	spec = {}
	plot_list = []
	cur_plot_index = -1

	for cmd in args:
		print(cmd)
		if cmd[0:7] == "xlabel=":
			spec["xlabel"] = cmd[7:]
		elif cmd[0:7] == "ylabel=":
			spec["ylabel"] = cmd[7:]
		elif cmd == "plot":
			plot_list += [{}]
			cur_plot_index += 1
		elif cmd[0:6] == "title=":
			plot_list[cur_plot_index]["title"] = cmd[6:]
		elif cmd[0:2] == "f=":
			plot_list[cur_plot_index]["fname"] = cmd[2:]

	spec["plotList"] = plot_list
	return json.dumps(spec)

def run():
	try:
		print('server running...')
		server_address = ('127.0.0.1', 8000)
		httpd = HTTPServer(server_address, MyServer)
		webbrowser.open('http://127.0.0.1:8000')
		print('server running...')
		httpd.serve_forever()
	except KeyboardInterrupt:
		print('server terminated')

if __name__ == '__main__':
	''' Usage: python3 server.py [data_path] [plot_specs] '''
	run()
