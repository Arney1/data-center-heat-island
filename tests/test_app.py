"""Smoke tests for the same navigation at both study sites."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class DashboardTests(unittest.TestCase):
    def test_every_page_for_both_sites(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/app.py"),
                                default_timeout=20).run()
        self.assertFalse(app.exception)
        for site in ("aws_pdx", "h5_quincy2"):
            app.sidebar.selectbox[0].set_value(site).run()
            for page in ("Overview", "Study area", "LST & spectral time series",
                         "Supervised classification", "Saved DIP artifacts"):
                with self.subTest(site=site, page=page):
                    app.sidebar.radio[0].set_value(page).run()
                    self.assertFalse(app.exception, [e.message for e in app.exception])
                    self.assertIn("Boardman" if site == "aws_pdx" else "Quincy", app.title[0].value)
                    if site == "h5_quincy2" and page == "Saved DIP artifacts":
                        self.assertTrue(any("never substituted" in item.value for item in app.info))


if __name__ == "__main__":
    unittest.main()
