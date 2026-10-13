# Modernisation Infrastructure & Sécurité

Dossier préparé pour le TP GitHub Projects. **Les données locales ne prouvent pas la création des objets GitHub.** Les URL et preuves sont à renseigner après publication et validation. Le dépôt `linux-admin-toolkit` existant est conservé.

## Synthèse de direction — fin de semaine 4

Hypothèse : démarrage le 14 septembre 2026 ; situation simulée au 9 octobre ; clôture le 4 décembre (12 semaines).

Le volume initial est de **69 jours-personnes** pour 15 tâches. Le correctif critique ajoute **2 jours**, soit **71 jours-personnes** pour 16 tâches. Les systèmes portent **18 jours**, les réseaux 15, la cybersécurité 14, la continuité d’activité 13 et la supervision 11. Les **systèmes** constituent donc la charge la plus importante.

Les audits et les deux migrations sont terminés : **6 tâches sur 16 (37,5 %)**, représentant **28 jours-personnes de charge estimée**. Trois tâches sont en cours, une bloquée et six à faire. Il reste 43 jours-personnes de charge attachée aux tâches non terminées ; cette valeur n’est pas une mesure du reste à faire, car le travail déjà effectué sur les tâches en cours n’est pas déduit.

Les risques élevés concernent les migrations, la segmentation, le pare-feu/VPN, les accès administrateurs, les sauvegardes, le PRA et la vulnérabilité exposée. Les principaux risques de retard sont la livraison du matériel réseau, le retard MFA et les dépendances du PRA. Relancer le fournisseur, fixer une date de livraison et réserver une fenêtre MFA avant S8.

Passer le correctif exposé et le MFA en priorité **Critique**. Réduire immédiatement l’exposition du serveur, sauvegarder, appliquer un correctif validé puis vérifier l’absence de vulnérabilité. Décaler si nécessaire la rédaction non urgente pour libérer la capacité ; préserver les tests de restauration et la recette finale.

Cette synthèse est calculée depuis `project.json`, source des données destinées à GitHub Projects. Elle doit être confrontée aux agrégations du projet après publication.

## Publication et livrables

1. Installer GitHub CLI et s’authentifier avec les droits dépôt et Projects (`gh auth login`, puis `gh auth refresh -s project`).
2. Exécuter `python3 scripts/publish-project.py --owner NKZ05`. L’outil crée un dépôt **public** `infra-modernisation`, les labels, jalons, issues, le projet et les champs ; il ne publie pas les fichiers ni les PR. Relire `docs/github-configuration.md` avant exécution.
3. Exécuter `python3 scripts/publish-interventions.py --merge` pour publier les sources, créer les branches (trois commits pour le disque, deux pour la sauvegarde), ouvrir les PR et les fusionner après les tests. L’identité Git doit être configurée. Les étapes détaillées sont dans `docs/interventions.md`.
4. Configurer les vues, graphiques et automatisations selon `docs/github-configuration.md` puis compléter `docs/livrables.md`.

L’outil refuse un dépôt déjà existant afin d’éviter les doublons. Il conserve un journal de progression sans secret dans `publication.json`. En cas d’échec partiel, vérifier les objets créés avant de reprendre manuellement ; ne pas supprimer un dépôt existant pour relancer.

## Interventions techniques

```bash
./scripts/check-disk.sh 80       # 0 : OK, 1 : seuil atteint, 2 : erreur
./scripts/backup.sh /chemin/source /chemin/destination
python3 -m unittest discover -s tests -v
```

Prérequis Linux : Bash, df, awk, tar, sha256sum, mktemp ; Python 3 pour les tests et la publication. Les scripts ne requièrent pas root. La sauvegarde crée une archive et un manifeste ; elle ne remplace pas une stratégie hors site ou un PRA testé.

## Automatisation proposée

Dans les workflows intégrés du Project : fermeture d’une issue → statut `Terminé`, réouverture → `À faire`. Une PR fusionnée comportant `Closes #NUMÉRO` ferme l’issue du même dépôt et déclenche cette mise à jour. Une référence `Refs #NUMÉRO` dans un commit assure le lien sans fermer l’issue. Les workflows doivent être activés et testés ; leur configuration locale n’est pas une preuve d’activation.
