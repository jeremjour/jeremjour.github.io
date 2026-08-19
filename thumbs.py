#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere les vignettes manquantes.  Usage : python3 thumbs.py   (pip install pillow)"""
import os
from PIL import Image

LARGEUR, QUALITE = 500, 75

for dossier in ('photos', 'evenements'):
    if not os.path.isdir(dossier):
        continue
    cible = os.path.join(dossier, 'thumbs')
    os.makedirs(cible, exist_ok=True)
    faits = 0
    for racine, dirs, fichiers in os.walk(dossier):
        if 'thumbs' in racine:
            continue
        for f in fichiers:
            if not f.lower().endswith(('.avif', '.jpg', '.jpeg', '.png', '.webp')):
                continue
            out = os.path.join(cible, os.path.splitext(f)[0] + '.avif')
            src = os.path.join(racine, f)
            if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
                continue
            im = Image.open(src).convert('RGB')
            im.thumbnail((LARGEUR, int(LARGEUR * 4 / 3)), Image.LANCZOS)
            im.save(out, 'AVIF', quality=QUALITE)
            faits += 1
            print('  ', out)
    print(f"{dossier} : {faits} vignette(s) generee(s)")
