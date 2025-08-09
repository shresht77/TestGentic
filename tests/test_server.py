"""Unit tests for the backend server.

These tests spin up an instance of the HTTP server in a background thread and
exercise the various endpoints to verify correct behaviour.  They rely only on
Python’s standard library and therefore can run in offline environments.
"""

import http.client
import json
import threading
import time
import unittest
from http.server import HTTPServer
from urllib.parse import urlencode

# Import the request handler from the backend.  The handler uses an absolute
# path to locate static files, so it does not matter what the current working
# directory is during the tests.
from backend.server import RequestHandler


def _find_free_port() -> int:
    """Find an available TCP port on localhost for the test server."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


class ServerTestCase(unittest.TestCase):
    """Test suite for the DPDP backend server."""

    @classmethod
    def setUpClass(cls) -> None:
        """Start the HTTP server on a free port before any tests run."""
        cls.port = _find_free_port()
        cls.httpd = HTTPServer(("localhost", cls.port), RequestHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()
        # Give the server a moment to start
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls) -> None:
        """Shut down the HTTP server after all tests have completed."""
        cls.httpd.shutdown()
        cls.thread.join()

    def _get(self, path: str) -> http.client.HTTPResponse:
        conn = http.client.HTTPConnection("localhost", self.port)
        conn.request("GET", path)
        return conn.getresponse()

    def _post(self, path: str, body: dict) -> http.client.HTTPResponse:
        conn = http.client.HTTPConnection("localhost", self.port)
        encoded = urlencode(body).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        conn.request("POST", path, body=encoded, headers=headers)
        return conn.getresponse()

    def test_health_endpoint(self) -> None:
        response = self._get("/health")
        self.assertEqual(response.status, 200)
        data = json.loads(response.read().decode())
        self.assertEqual(data.get("status"), "ok")

    def test_root_serves_index(self) -> None:
        response = self._get("/")
        self.assertEqual(response.status, 200)
        body = response.read().decode()
        # The index page contains the consent form heading
        self.assertIn("DPDP Hotel Compliance", body)

    def test_consent_capture_success(self) -> None:
        response = self._post(
            "/consent/capture",
            {"guestName": "Alice", "guestEmail": "alice@example.com"},
        )
        self.assertEqual(response.status, 200)
        data = json.loads(response.read().decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Consent captured successfully")

    def test_consent_capture_empty(self) -> None:
        # Even empty submissions should return a success message
        response = self._post("/consent/capture", {})
        self.assertEqual(response.status, 200)
        data = json.loads(response.read().decode())
        self.assertEqual(data["message"], "Consent captured successfully")

    def test_invalid_post_returns_404(self) -> None:
        response = self._post("/unknown", {"foo": "bar"})
        self.assertEqual(response.status, 404)

    def test_dpdp_requirements_page(self) -> None:
        response = self._get("/dpdp-requirements")
        self.assertEqual(response.status, 200)
        body = response.read().decode()
        self.assertIn("Digital Personal Data Protection", body)


if __name__ == "__main__":
    unittest.main()
