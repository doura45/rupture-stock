# Guide du Débutant : Prévision avec Prophet

Tu t'es déjà demandé comment Amazon ou Carrefour savent exactement combien de produits mettre dans leurs rayons la semaine prochaine ? Ils utilisent des modèles de séries temporelles (Time Series). 
Pour ce projet, j'ai utilisé **Prophet**, un modèle très puissant créé par Facebook.

---

### 1. Qu'est-ce qu'une Série Temporelle ?
C'est tout simplement une suite de données mesurées dans le temps.
Ici, ma donnée est : "Combien de fois a-t-on commandé le produit X aujourd'hui ?"
Pour que Prophet fonctionne, je dois lui donner un tableau avec deux colonnes exactes :
- `ds` : La date (ex: 2016-12-01)
- `y` : La demande mesurée ce jour-là.

### 2. Comment fonctionne Prophet ?
Contrairement à de l'Intelligence Artificielle "boîte noire", Prophet est un modèle statistique transparent qui décompose le problème en trois parties :
1. **La Tendance globale** : Est-ce qu'on vend globalement de plus en plus, ou de moins en moins ?
2. **La Saisonnalité** : Est-ce qu'on vend plus en fin d'année ? Plus le vendredi ?
3. **Les Vacances/Jours fériés** : Des événements spéciaux.

### 3. Les Intervalles de Confiance (La vraie magie)
C'est le cœur de mon analyse pour la gestion des stocks !
Quand Prophet prédit l'avenir, il ne donne pas qu'un seul chiffre. Il dit : *"Je pense qu'on vendra 100 produits (`yhat`), mais je suis sûr à 95% que ça ne dépassera pas 130 produits (`yhat_upper`)."*

**Mon action métier** : 
En tant que responsable de l'approvisionnement, le chiffre 100 ne m'intéresse pas. Si je commande 100 produits et qu'il y a un pic à 120, je suis en **rupture de stock**. Je vais donc utiliser le chiffre 130 (`yhat_upper`) comme objectif de stock. La différence entre 130 et 100, c'est ce qu'on appelle le **Stock de Sécurité**.
