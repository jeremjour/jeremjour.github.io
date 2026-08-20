# Ajouter des photos — mode d'emploi

Tout se fait sur github.com, dans le navigateur. Rien à installer.

---

## Cas 1 — Ajouter des photos à un album existant

**C'est tout ce qu'il y a à faire :**

1. Sur GitHub, ouvre le dossier de l'album — par exemple `photos/islande/`
2. Bouton **`Add file`** → **`Upload files`**
3. Glisse tes photos, puis **`Commit changes`**

Le robot fait le reste : vignettes, page de l'album, sitemap. Compte 1 à 2 minutes.

> Tes photos apparaîtront avec la légende de l'album (« Islande »). Si tu veux une légende
> précise par photo, voir le cas 3.

---

## Cas 2 — Créer un nouvel album

**Étape A — déposer les photos**

1. `Add file` → `Upload files`
2. **Avant** de lâcher tes fichiers, clique dans le champ du chemin en haut et tape :
   `photos/pyrenees/`
3. Glisse les photos, `Commit changes`

**Étape B — nommer l'album**

1. Ouvre `site.config.json`, clique sur le crayon ✏️
2. Trouve la ligne `"albums": [`
3. Juste après, colle ce bloc (en gardant la virgule à la fin) :

```json
    {
      "slug": "pyrenees",
      "titre": "Pyrénées",
      "sous_titre": "Cirque de Gavarnie",
      "description": "Sommets et cirques des Pyrénées, au sol et par drone.",
      "couverture": "photos/pyrenees/NOM-DE-TA-PHOTO.avif",
      "photos": []
    },
```

4. Remplace `pyrenees`, `Pyrénées`, les deux textes, et le nom de la photo de couverture
5. `Commit changes`

Laisse `"photos": []` vide — le robot détecte tes fichiers tout seul.

---

## Cas 3 — Légendes précises (optionnel)

Par défaut chaque photo porte le nom de l'album. Pour une légende sur mesure,
ajoute-la entre les crochets de `"photos"` :

```json
      "photos": [
        { "src": "photos/pyrenees/gavarnie-01.avif", "label": "Cirque de Gavarnie", "alt": "Cascade du cirque de Gavarnie au lever du jour, Hautes-Pyrénées" }
      ]
```

- `label` = ce qui s'affiche au survol de la photo
- `alt` = la description lue par Google Images (soigne-la, c'est du référencement)

---

## Cas 4 — Changer les photos de la page d'accueil

Dans `site.config.json`, section `"accueil"` → `"selection"`.
C'est une simple liste de chemins. Ajoute, retire, réordonne.
L'ordre de la liste = l'ordre d'affichage.

---

## Vérifier que le robot a bien tourné

Onglet **`Actions`** en haut du dépôt.

| Pastille | Signification |
|---|---|
| 🟡 | en cours, patiente |
| ✅ | terminé, le site est à jour |
| ❌ | erreur — clique dessus pour lire le message |

---

## Règles à respecter

- **Un dossier par album**, nommé comme le `slug` : `photos/<slug>/`
- **Noms de fichiers** sans accent ni espace : `gavarnie-01.avif`, pas `Gavarnie 01.avif`
- **Ne touche pas** aux dossiers `thumbs/`, ni aux fichiers `index.html`, `albums/`, `sitemap.xml` — le robot les réécrit
- **Dans le JSON** : chaque bloc se termine par une virgule, sauf le dernier de la liste

Si le JSON casse, l'onglet Actions affiche ❌ et le site reste sur sa version précédente.
Rien n'est perdu.
