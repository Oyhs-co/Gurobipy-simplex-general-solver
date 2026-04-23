#!/usr/bin/env python
"""
Punto de entrada principal para el solver de programacion lineal.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
