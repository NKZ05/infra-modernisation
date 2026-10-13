# Deux interventions et traçabilité

L’outil `python3 scripts/publish-interventions.py --merge` automatise les étapes ci-dessous après la création des objets GitHub. Il reproduit le défaut de seuil avant la correction, valide les scripts et conserve les commits en fusionnant les PR. Il garde son clone temporaire et les liens dans `publication.json`. Les étapes restent à exécuter dans un clone du **nouveau** dépôt. Les scripts présents ici sont les versions finales ; aucune branche, aucun commit ni aucune PR n’est présenté comme déjà publié.

## Préparer le dépôt

Après publication des issues, cloner l’URL inscrite dans `publication.json` dans un dossier voisin. Copier README.md, project.json, docs/ et le script de publication dans le clone, puis créer un commit initial sur `main` et pousser. Ne pas inclure d’abord les deux scripts techniques et leurs tests : ils doivent être introduits par leurs branches dédiées.

Lire les numéros réels des issues locales 11 et 14 dans `publication.json`. Dans les messages suivants remplacer `NUM_DISQUE` et `NUM_SAUVEGARDE` par ces numéros ; ce ne sont pas des numéros supposés.

## Contrôle disque — trois étapes réelles

1. `git switch -c feature/controle-disque`
2. Ajouter une première version de `scripts/check-disk.sh` avec `df -Pk`, lecture du pourcentage et seuil strict `>` ; commit `feat: contrôler les seuils disque — Refs #NUM_DISQUE`.
3. Ajouter la validation du seuil, les codes de sortie et les tests sous le seuil, disque plein et seuil invalide ; commit `test: valider les entrées et erreurs du contrôle disque — Refs #NUM_DISQUE`.
4. Simuler le défaut de la première version : à 80 % avec seuil 80, le script renvoie OK. Corriger `>` en `>=`, ajouter le test d’égalité et le cas `080`. La version finale doit être celle fournie. Commit `fix: alerter dès le seuil exact et accepter 080 — Refs #NUM_DISQUE`.
5. Lancer les tests ; pousser la branche ; ouvrir une PR vers `main`, corps : description, résultats de tests, `Closes #NUM_DISQUE`.

## Sauvegarde — deux étapes réelles

1. Depuis main : `git switch -c feature/sauvegarde-verifiee`.
2. Ajouter une version créant une archive tar dans un dossier temporaire ; commit `feat: archiver un répertoire de sauvegarde — Refs #NUM_SAUVEGARDE`.
3. Ajouter le manifeste SHA-256, sa vérification, le nettoyage sur erreur, le refus des destinations imbriquées et les tests de restauration. Commit `feat: vérifier l’intégrité et sécuriser la destination — Refs #NUM_SAUVEGARDE`.
4. Tester et pousser ; ouvrir une PR vers `main` avec `Closes #NUM_SAUVEGARDE` et les résultats de restauration.

Ne pas copier des tests qui ciblent le script de l’autre branche avant sa fusion ; séparer les classes de tests en fichiers si nécessaire. Pour chaque PR : examiner le diff, valider les critères de l’issue, puis fusionner avec **Create a merge commit** pour conserver les étapes distinctes (éviter squash). Conserver les URL et identifiants des commits dans `livrables.md`.

Depuis chaque issue, vérifier les références aux commits, la PR liée, puis la fermeture après fusion et le statut du Project. Mettre à jour la photographie de validation sans remplacer la simulation S4.
