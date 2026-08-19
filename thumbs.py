#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genere les vignettes manquantes ou perimees.

Usage : python3 thumbs.py

Une vignette est regeneree si :
  - elle n'existe pas
  - son ratio ne correspond plus a celui de l'original  (recadrage modifie)
  - sa largeur n'est pas la largeur cible
  - l'original est plus recent qu'elle

Le controle du ratio est essentiel : les dates de fichiers ne sont pas fiables
apres un upload via l'interface web de GitHub, qui les aligne toutes.
"""
import os
from PIL import Image

LARGEUR = 500
QUALITE = 75
EXT = ('.avif', '.jpg', '.jpeg', '.png', '.webp')
TOLERANCE = 0.01


def doit_regenerer(src, out):
    if not os.path.exists(out):
        return True, "absente"
    try:
        o = Image.open(src); v = Image.open(out)
    except Exception:
        return True, "illisible"
    r_src = o.size[0] / o.size[1]
    r_out = v.size[0] / v.size[1]
    if abs(r_src - r_out) > TOLERANCE:
        return True, f"ratio {r_out:.3f} != original {r_src:.3f}"
    # taille attendue : calculee exactement comme le fait Image.thumbnail()
    calc = Image.new('RGB', o.size)
    calc.thumbnail((LARGEUR, int(LARGEUR * 4 / 3)), Image.LANCZOS)
    if v.size != calc.size:
        return True, f"taille {v.size[0]}x{v.size[1]} != {calc.size[0]}x{calc.size[1]}"
    if os.path.getmtime(src) > os.path.getmtime(out):
        return True, "original plus recent"
    return False, ""


def main():
    total = 0
    for dossier in ('photos', 'evenements'):
        if not os.path.isdir(dossier):
            continue
        cible = os.path.join(dossier, 'thumbs')
        os.makedirs(cible, exist_ok=True)
        faits = 0
        for racine, dirs, fichiers in os.walk(dossier):
            dirs[:] = [d for d in dirs if d != 'thumbs']
            for f in sorted(fichiers):
                if not f.lower().endswith(EXT) or f.startswith('.'):
                    continue
                src = os.path.join(racine, f)
                out = os.path.join(cible, os.path.splitext(f)[0] + '.avif')
                besoin, raison = doit_regenerer(src, out)
                if not besoin:
                    continue
                im = Image.open(src).convert('RGB')
                im.thumbnail((LARGEUR, int(LARGEUR * 4 / 3)), Image.LANCZOS)
                im.save(out, 'AVIF', quality=QUALITE)
                print(f"   {out}  ({raison})  -> {im.size[0]}x{im.size[1]}")
                faits += 1
        print(f"{dossier} : {faits} vignette(s) regeneree(s)")
        total += faits

    for dossier in ('photos', 'evenements'):
        cible = os.path.join(dossier, 'thumbs')
        if not os.path.isdir(cible):
            continue
        originaux = set()
        for racine, dirs, fichiers in os.walk(dossier):
            dirs[:] = [d for d in dirs if d != 'thumbs']
            for f in fichiers:
                if f.lower().endswith(EXT):
                    originaux.add(os.path.splitext(f)[0])
        for f in sorted(os.listdir(cible)):
            if os.path.splitext(f)[0] not in originaux:
                os.remove(os.path.join(cible, f))
                print(f"   supprimee (orpheline) : {cible}/{f}")

    if total == 0:
        print("Toutes les vignettes sont a jour.")


if __name__ == '__main__':
    main()
