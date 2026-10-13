# Configuration GitHub Projects

Les données et les six vues sont publiées. Les types de vues, champs visibles et filtres sont configurés via l’API. Les regroupements, sommes, champs de dates de la roadmap et les graphiques ne sont pas configurables par les mutations exposées : ils restent à finaliser dans l’interface. Utiliser `publication.json` pour ouvrir le projet et retrouver les issues. Le dépôt et le Project sont publics pour permettre l’accès à l’enseignant. Ne pas y déposer de secrets ni de données d’infrastructure réelle.

## Champs

L’outil crée Priorité (Critique/Haute/Normale/Basse), Domaine technique (cinq domaines), Charge estimée (nombre de jours-personnes), Risque (Élevé/Moyen/Faible), deux champs Date et Avancement (À faire/En cours/Bloqué/Terminé).

GitHub conserve le nom natif **Status**. Les sept champs personnalisés sont présents, dont **Avancement**, et les deux statuts portent les mêmes valeurs grâce à `scripts/sync-status.py`. Utiliser Status pour le Kanban natif et Avancement pour les analyses demandées. Après tout changement manuel, mettre les deux champs à jour ou relancer la synchronisation.

## Quatre vues à enregistrer

| Vue | Configuration | Informations affichées |
|---|---|---|
| Tableau opérationnel | Board ; grouper par Status | Priorité, Domaine technique, Risque, Charge estimée, Date de fin prévue |
| Suivi des charges | Table ; grouper par Domaine technique ; Field sum → Charge estimée | Charge, priorité, risque, avancement ; total par groupe |
| Roadmap | Roadmap ; début = Date de début ; fin = Date de fin prévue ; zoom mensuel, septembre–décembre 2026 | Grouper par milestone ; afficher les dates et les dépendances dans les issues |
| Synthèse de direction | Table ; filtre `is:open` ; grouper par Priorité | Risque, avancement, dates et jalon ; trier par date de fin |

La vue direction conserve toutes les interventions ouvertes et met Critique/Haute en tête. Ajouter une vue complémentaire « Risques élevés » avec le filtre `is:open Risque:Élevé`. Si un nom contient des espaces, sélectionner le champ avec l’autocomplétion de l’interface pour obtenir la syntaxe exacte.

Suivi des charges : activer les sommes dans les en-têtes de groupes. Pour un total global, créer une vue Table « Charge globale » sans regroupement et vérifier le total via Insights (Y = somme de Charge estimée, sans filtre). Valeurs attendues : Systèmes 18, Réseaux 15, Cybersécurité 14, Supervision 11, Continuité 13 ; total 71. Ne pas filtrer les issues fermées dans ces vues.

## Insights

Créer trois graphiques actuels, sans filtre excluant les issues fermées. Pour la photographie S4, les valeurs de référence sont ci-dessous ; le Project actuel comporte ensuite deux interventions terminées de plus :

1. « Répartition par domaine » : barres, X = Domaine technique, Y = nombre d’items. Résultat : 3 / 3 / 4 / 3 / 3.
2. « Avancement S4 » : barres, X = Avancement, Y = nombre d’items. Résultat : À faire 6, En cours 3, Bloqué 1, Terminé 6.
3. « Priorités et risques » : barres, X = Priorité, group by = Risque, Y = nombre d’items. Résultat : Critique 2, Haute 14 ; risques Élevé 10 et Moyen 6.

Ajouter si possible « Charge par domaine » : X = Domaine technique, Y = somme de Charge estimée. Tous ces graphiques doivent utiliser directement les items du Project. Selon le forfait du compte, la création de plusieurs graphiques peut être limitée : vérifier l’accès à Insights avant de considérer le livrable terminé.

## Simulation et automatisation

Les données publiées représentent déjà la fin S4 ; les détails des reports se trouvent dans `planification.md`. La vulnérabilité est un scénario pédagogique, pas un diagnostic réel.

Le workflow intégré « Auto-add sub-issues to project » est confirmé actif. « Item closed » est désactivé ; l’activer et choisir Terminé sur le champ natif Status. Vérifier dans l’interface si un workflow de réouverture est disponible avant de le configurer. Après fusion des deux PR, vérifier la fermeture des issues 11 et 14 (identifiants locaux) et la mise à jour de leurs items. Il y aura alors 8 tâches terminées, 3 en cours, 1 bloquée et 4 à faire : cet état technique est postérieur à la photographie S4. Préserver la synthèse S4 comme historique et dater la nouvelle validation.

Vérifier l’accès enseignant en ouvrant les URL dans une fenêtre privée ; enregistrer des captures des quatre vues, des trois graphiques et des workflows.

Références : [API Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects), [configuration Insights](https://docs.github.com/en/issues/planning-and-tracking-with-projects/viewing-insights-from-your-project/configuring-charts).
