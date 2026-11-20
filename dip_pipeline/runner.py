"""Compatibility entry point for the local artifact audit.

Reading saved CSV/JSON files never verifies imagery or completes research.
"""
from .audit import main


def run_dip_audit():
    return main()


if __name__ == "__main__":
    run_dip_audit()
