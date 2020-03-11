#!/usr/bin/env python

from torchember.app import app
import argparse
import logging
import os
ap = argparse.ArgumentParser()
ap.add_argument("--port", default=8080, type=int, dest="port")
args = ap.parse_args()

logging.info(f"Torch Ember Running on port {args.port}")
def run():
    app.run(host="0.0.0.0", port=args.port, debug=False)