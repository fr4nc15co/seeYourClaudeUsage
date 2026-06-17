#!/usr/bin/env python3
"""Arranca el servidor del panel de costes y abre el navegador."""

import os, sys, threading, time, webbrowser

ROOT = os.path.dirname(os.path.realpath(__file__))
PANEL_DIR = os.path.join(ROOT, "panel_costes")
sys.path.insert(0, PANEL_DIR)

def _abrir_browser(puerto):
    time.sleep(2)
    webbrowser.open("http://localhost:%d/analisisClaude" % puerto)

puerto = 8799
_args = sys.argv[1:]
for i, a in enumerate(_args):
    if a == "--puerto" and i + 1 < len(_args):
        try:
            puerto = int(_args[i + 1])
        except ValueError:
            pass

threading.Thread(target=_abrir_browser, args=(puerto,), daemon=True).start()

import servidor
servidor.main()
