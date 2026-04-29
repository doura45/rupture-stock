# Guide du Débutant : Explorer les Données de Demande

Pour bien gérer des stocks, il faut comprendre ce qui s'est passé avant d'essayer de deviner ce qui va se passer. C'est l'objectif de l'exploration de données.

---

### 1. Nettoyer les données (Data Cleaning)
Dans la vraie vie, les bases de données sont souvent "sales". 
Dans notre fichier, la colonne de demande contenait parfois des parenthèses autour des chiffres (ex: `(150)`). J'ai utilisé des expressions régulières (Regex) avec Pandas pour nettoyer ces valeurs et les transformer en vrais nombres avec lesquels on peut faire des maths.

### 2. Le Coefficient de Variation (CV)
C'est la découverte majeure de mon analyse.
- **La Moyenne** : Indique combien de produits on vend en moyenne par mois.
- **L'Écart-Type** : Mesure si on s'éloigne beaucoup de cette moyenne.
- **Le CV (Écart-type / Moyenne)** : C'est ce qui indique le risque de rupture ! Si je vends 100 produits par mois sans exception (CV bas), c'est facile à gérer. Si je vends 10 produits un mois et 190 le mois suivant (CV haut), je suis en danger de rupture.
- J'ai combiné le volume global et le CV pour cibler les 10 produits les plus "dangereux" de notre catalogue.

### 3. Les Entrepôts
L'analyse a immédiatement montré qu'un seul entrepôt (`Whse_J`) supportait l'immense majorité des commandes. En termes de Supply Chain, c'est un risque critique (Single Point of Failure). Il faut auditer cet entrepôt en priorité.
