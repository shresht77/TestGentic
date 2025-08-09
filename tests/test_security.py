import unittest
import threading
import socket
import urllib.request
import urllib.error

from backend.server import RequestHandler
import socketserver

class TestSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start server in background thread on a free port
        cls.port = 8001
        handler = RequestHandler
        cls.httpd = socketserver.TCPServer(("", cls.port), handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.thread.join()

    def test_path_traversal_not_allowed(self):
        # Attempt to access a file outside the frontend directory should return 404
        url = f'http://localhost:{self.port}/../README.md'
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(url)
        self.assertEqual(context.exception.code, 404)

    def test_invalid_method_returns_error(self):
        # DELETE requests are not supported; server should return 405 or 501
        req = urllib.request.Request(f'http://localhost:{self.port}/', method="DELETE")
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req)
        self.assertIn(context.exception.code, (405, 501))

if __name__ == '__main__':
    unittest.main()
