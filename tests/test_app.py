import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app import create_app


class FormTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.data_file = Path(self.directory.name) / "datos_prueba.txt"
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "clave-solo-para-tests",
            "DATA_FILE": self.data_file,
        })
        self.client = self.app.test_client()
        self.client.get("/")
        with self.client.session_transaction() as session:
            self.token = session["csrf_token"]

    def submit(self, **changes):
        data = {
            "csrf_token": self.token,
            "visitante": "Visitante de prueba",
            "referencia": "DEMO-001",
        }
        data.update(changes)
        return self.client.post("/guardar", data=data)

    def test_save_append_and_thank_you_without_resubmission(self):
        response = self.submit(visitante="  Visitante Ñ  ")
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.location, "/gracias")
        self.assertIn("¡Gracias", self.client.get(response.location).text)
        self.client.get(response.location)
        self.assertEqual(len(self.data_file.read_text(encoding="utf-8").splitlines()), 1)
        self.submit(referencia="DEMO-002")
        records = [json.loads(line) for line in self.data_file.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(records, [
            {"visitante": "Visitante Ñ", "referencia": "DEMO-001"},
            {"visitante": "Visitante de prueba", "referencia": "DEMO-002"},
        ])

    def test_invalid_and_missing_csrf_do_not_write(self):
        for token in ("", "incorrecto", "ñ"):
            with self.subTest(token=token):
                self.assertEqual(self.submit(csrf_token=token).status_code, 400)
        self.assertFalse(self.data_file.exists())

    def test_invalid_values_do_not_write(self):
        for changes in (
            {"visitante": "   "},
            {"visitante": "a" * 61},
            {"referencia": ""},
            {"referencia": "a" * 41},
            {"referencia": "demo\nregistro falso"},
            {"visitante": "demo\x00prueba"},
        ):
            with self.subTest(changes=changes):
                self.assertEqual(self.submit(**changes).status_code, 400)
        self.assertFalse(self.data_file.exists())

    def test_extra_and_duplicate_fields_do_not_write(self):
        self.assertEqual(self.submit(otro="dato extra").status_code, 400)
        self.assertEqual(self.submit(visitante=["uno", "dos"]).status_code, 400)
        self.assertFalse(self.data_file.exists())

    def test_error_values_are_html_escaped(self):
        response = self.submit(visitante='<script>alert("demo")</script>', referencia="")
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('<script>alert("demo")</script>', response.text)
        self.assertIn("&lt;script&gt;", response.text)

    def test_write_failure_does_not_show_success(self):
        with patch("app.save_record", side_effect=OSError("disco no disponible")):
            response = self.submit()
        self.assertEqual(response.status_code, 503)
        self.assertIn("No se pudo guardar", response.text)
        self.assertFalse(self.data_file.exists())

    def test_static_resources_and_private_storage(self):
        for path in (
            "/static/css/styles.css", "/static/js/demo.js",
            "/static/img/logos/logo-principal.svg", "/static/img/logos/logo-secundario.svg",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                response.close()
        self.submit()
        for path in ("/datos_prueba.txt", "/static/../datos_prueba.txt"):
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_oversized_request_is_rejected(self):
        self.assertEqual(self.submit(visitante="a" * 20000).status_code, 413)
        self.assertFalse(self.data_file.exists())


if __name__ == "__main__":
    unittest.main()
