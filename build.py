"""Rebuild everything generated from the sources, in order:
legal pages -> SEO metadata / sitemap -> single-file HTML versions.
Usage:  python3 build.py
"""
import os
import subprocess
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
for script in ("build-legal.py", "build-seo.py", "build-standalone.py"):
    print(f"== {script}")
    subprocess.run([sys.executable, script], check=True)
