from setuptools import setup
import subprocess
import sys
import os


def run_bootstrap():
    bootstrap = os.path.join(os.path.dirname(__file__), "scripts", "bootstrap.py")
    if os.path.exists(bootstrap):
        subprocess.run([sys.executable, bootstrap], check=True)


setup()

# if __name__ == "__main__" and "build_meta" not in sys.modules:
#    run_bootstrap()
