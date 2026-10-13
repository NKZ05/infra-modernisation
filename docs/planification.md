# Planification après simulation S4

Les identifiants ci-dessous sont locaux ; les numéros GitHub sont enregistrés par l’outil de publication. Début : 14 septembre 2026 ; fin S4 : 9 octobre ; fin S12 : 4 décembre. Les charges sont des jours-personnes, distincts des durées calendaires.

| ID | Travail | Domaine | Jours | Statut | Dates | Dépendances |
|---|---|---|---:|---|---|---|
| 1 | Inventorier les serveurs et systèmes obsolètes | Systèmes | 4 | Terminé | 2026-09-14 → 2026-09-25 | — |
| 2 | Migrer le serveur de fichiers | Systèmes | 6 | Terminé | 2026-09-28 → 2026-10-09 | 1 |
| 3 | Migrer le serveur applicatif | Systèmes | 8 | Terminé | 2026-09-28 → 2026-10-09 | 1 |
| 4 | Auditer les flux et équipements des deux sites | Réseaux | 3 | Terminé | 2026-09-14 → 2026-09-25 | — |
| 5 | Segmenter le réseau en VLAN | Réseaux | 7 | Bloqué | 2026-10-12 → 2026-10-30 | 4 |
| 6 | Déployer le pare-feu intersites et le VPN | Réseaux | 5 | À faire | 2026-11-02 → 2026-11-13 | 5 |
| 7 | Auditer les vulnérabilités et comptes privilégiés | Cybersécurité | 4 | Terminé | 2026-09-14 → 2026-09-25 | — |
| 8 | Déployer le MFA pour les administrateurs | Cybersécurité | 5 | En cours | 2026-10-19 → 2026-11-06 | 7 |
| 9 | Formaliser la réponse aux incidents de sécurité | Cybersécurité | 3 | À faire | 2026-11-09 → 2026-11-20 | 7 |
| 10 | Centraliser les journaux des serveurs | Supervision | 5 | En cours | 2026-10-05 → 2026-10-23 | 1, 4 |
| 11 | Créer un contrôle des seuils disque | Supervision | 2 | À faire | 2026-10-12 → 2026-10-16 | 1 |
| 12 | Configurer les alertes de disponibilité | Supervision | 4 | À faire | 2026-10-26 → 2026-11-13 | 10, 11 |
| 13 | Auditer les sauvegardes et définir RPO/RTO | Continuité d’activité | 3 | Terminé | 2026-09-14 → 2026-09-25 | — |
| 14 | Automatiser une sauvegarde avec contrôle d’intégrité | Continuité d’activité | 4 | À faire | 2026-10-12 → 2026-10-23 | 13 |
| 15 | Tester le PRA et valider la mise en production | Continuité d’activité | 6 | À faire | 2026-11-23 → 2026-12-04 | 2, 3, 6, 8, 9, 12, 14, 16 |
| 16 | Corriger une vulnérabilité critique sur le serveur exposé | Cybersécurité | 2 | En cours | 2026-10-12 → 2026-10-16 | 7 |

Les migrations peuvent avancer en parallèle après l’inventaire ; les audits réseau, sécurité et sauvegardes sont indépendants. En S5, le correctif urgent, le contrôle disque et la sauvegarde peuvent avancer en parallèle avec plusieurs intervenants. Avec un seul intervenant, prioriser le correctif et décaler les tâches non critiques.

Le VLAN prévu initialement S3–S6 est reporté S5–S7 : matériel non livré, relance fournisseur et confirmation de livraison nécessaires avant démarrage. Le jalon infrastructure reste en S6 ; le VLAN et le pare-feu appartiennent au jalon sécurité S10. Le MFA passe de S3–S5 à S6–S8 faute de disponibilité des intervenants. La vulnérabilité est découverte en S4 et traitée en priorité dès S5 ; le confinement commence immédiatement dans le scénario.
