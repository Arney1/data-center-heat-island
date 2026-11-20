"""Supervised land-cover classification; regression and SHAP are future work."""

from .supervised_classification import LandCoverClassifier
from .dataset import MLDatasetManager

__all__ = ["LandCoverClassifier", "MLDatasetManager"]
