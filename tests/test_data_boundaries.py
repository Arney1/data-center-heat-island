"""Regresi: pisahkan lokasi serta data pengamatan dari data sintetis."""

import io
import unittest
from unittest.mock import patch

import pandas as pd

from dip_pipeline.config import SITES
from dip_pipeline.gee_fetcher import GEEDataFetcher
from dip_pipeline.timeseries import load_zonal_timeseries


HEADER = "tahun,zona,LST,LSTanom,NDVI,NDBI,EMIS"
ROW = "2025,0_tapak_penuh,40,2,0.1,0.2,0.97"


def offline_fetcher(site_id):
    fetcher = GEEDataFetcher.__new__(GEEDataFetcher)
    fetcher.site_id = site_id
    fetcher.site_info = SITES[site_id]
    fetcher.site_name = fetcher.site_info["campus_name"]
    fetcher.campus_centroid = fetcher.site_info["campus_centroid"]
    fetcher.control_pair_centroid = fetcher.site_info["control_pair_centroid"]
    fetcher.is_authenticated = False
    return fetcher


class TimeseriesValidationTests(unittest.TestCase):
    def test_export_accepts_extra_columns_and_preserves_missing_values(self):
        frame = load_zonal_timeseries(io.StringIO(HEADER + ",.geo\n" + ROW + ",{}\n"
                                                  + "2024,0_tapak_penuh,39,,0.1,0.2,0.97,{}"),
                                     "h5_quincy2")
        self.assertEqual(frame.tahun.tolist(), [2024, 2025])
        self.assertTrue(pd.isna(frame.iloc[0].LSTanom))
        self.assertTrue(frame.site_id.eq("h5_quincy2").all())

    def test_wrong_site_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "bukan hasil lokasi"):
            load_zonal_timeseries(io.StringIO(HEADER + ",site_id\n" + ROW + ",aws_pdx"), "h5_quincy2")

    def test_duplicate_year_zone_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplikat"):
            load_zonal_timeseries(io.StringIO(HEADER + "\n" + ROW + "\n" + ROW), "h5_quincy2")

    def test_invalid_year_and_non_numeric_metric_are_rejected(self):
        for row in (ROW.replace("2025", "2025.5"), ROW.replace(",40,", ",panas,"),
                    ROW.replace(",40,", ",inf,")):
            with self.subTest(row=row), self.assertRaises(ValueError):
                load_zonal_timeseries(io.StringIO(HEADER + "\n" + row), "h5_quincy2")


class FetcherBoundaryTests(unittest.TestCase):
    def test_unknown_site_does_not_silently_select_boardman(self):
        with self.assertRaisesRegex(ValueError, "Lokasi tidak dikenal"):
            GEEDataFetcher(site_id="quincy_typo")

    def test_quincy_epochs_require_verified_configuration(self):
        with self.assertRaisesRegex(ValueError, "belum diverifikasi"):
            offline_fetcher("h5_quincy2").fetch_epoch_composites()

    def test_boardman_epoch_remains_authentication_gated(self):
        with self.assertRaisesRegex(RuntimeError, "tidak terautentikasi"):
            offline_fetcher("aws_pdx").fetch_epoch_composites()

    def test_missing_quincy_cache_never_reads_boardman(self):
        with patch("dip_pipeline.gee_fetcher.os.path.exists", return_value=False), \
                patch("dip_pipeline.gee_fetcher.pd.read_csv") as read:
            with self.assertRaisesRegex(FileNotFoundError, "h5_quincy2_timeseries.csv"):
                offline_fetcher("h5_quincy2").fetch_live_zonal_timeseries()
            read.assert_not_called()

    def test_quincy_cache_loads_only_its_own_file(self):
        with patch("dip_pipeline.gee_fetcher.os.path.exists", return_value=True), \
                patch("dip_pipeline.gee_fetcher.load_zonal_timeseries",
                      return_value=pd.DataFrame({"LST": [40]})) as load:
            result = offline_fetcher("h5_quincy2").fetch_live_zonal_timeseries()
            self.assertTrue(load.call_args.args[0].endswith("h5_quincy2_timeseries.csv"))
            self.assertEqual(load.call_args.args[1], "h5_quincy2")
            self.assertEqual(result.site_name.iloc[0], "H5 Quincy II")

    def test_offline_sampling_does_not_generate_or_overwrite_data(self):
        with patch.object(pd.DataFrame, "to_csv") as write:
            with self.assertRaisesRegex(RuntimeError, "autentikasi GEE"):
                offline_fetcher("h5_quincy2").extract_ml_feature_dataset()
            write.assert_not_called()

    def test_demo_is_explicit_labeled_and_site_specific(self):
        with patch.object(pd.DataFrame, "to_csv") as write, \
                patch("dip_pipeline.gee_fetcher.os.makedirs"):
            frame = offline_fetcher("h5_quincy2").extract_ml_feature_dataset(
                n_samples=12, allow_synthetic=True)
            self.assertTrue(frame.data_source.eq("synthetic_demo").all())
            self.assertTrue(frame.site_id.eq("h5_quincy2").all())
            self.assertTrue(write.call_args.args[0].endswith("ml_feature_dataset_h5_quincy2_synthetic.csv"))

    def test_live_failure_does_not_generate_synthetic_data(self):
        fetcher = offline_fetcher("h5_quincy2")
        fetcher.is_authenticated = True
        with patch("dip_pipeline.gee_fetcher.ee") as backend, \
                patch.object(pd.DataFrame, "to_csv") as write:
            backend.Image.side_effect = RuntimeError("GEE unavailable")
            with self.assertRaisesRegex(RuntimeError, "tidak diganti data sintetis"):
                fetcher.extract_ml_feature_dataset()
            write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
