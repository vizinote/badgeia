---
title: "AI Act : le guide du dirigeant de PME"
author: Brozapi
date: 2026-08-19
version: "1.0"
---

# AI Act : le guide du dirigeant de PME

**Comment lire ce guide**  
Ce document est écrit pour un dirigeant de petite entreprise ou d'association qui n'a pas de juriste interne. Il vise à donner une vue d'ensemble claire des obligations de transparence imposées par le règlement européen sur l'intelligence artificielle — l'« AI Act » — et à proposer des actions concrètes, vérifiables, sans jargon inutile.

**Mise en garde liminaire**  
Ce guide est une aide à la compréhension, pas un conseil juridique. Les règles évoluent, leur interprétation relève des autorités nationales et des tribunaux. Aucun outil, badge ou PDF ne peut à lui seul garantir la conformité de votre organisation.

---

## Introduction : pourquoi l'AI Act concerne aussi les petites structures

L'AI Act (règlement (UE) 2024/1689) est entré en application progressivement. Pour la plupart des sites web de PME, la date à retenir est le **2 août 2026** : à partir de cette date, les obligations de transparence de l'article 50 s'appliquent aux systèmes d'IA qui interagissent avec le public.

Concrètement, si votre site utilise un chatbot, un assistant conversationnel, un générateur de texte ou d'image, ou si vous publiez des contenus créés par une IA, vous devrez probablement informer vos visiteurs.

L'objectif du règlement n'est pas de bloquer l'innovation. Il est de permettre aux utilisateurs de savoir quand ils interagissent avec une IA et de distinguer ce qui est généré artificiellement de ce qui ne l'est pas. Cette transparence est présentée comme un moyen de renforcer la confiance et de réduire les risques de manipulation.

Pour une PME, l'enjeu est double :

1. **Éviter les risques réputationnels** : un client qui découvre qu'il a parlé à un chatbot sans le savoir peut se sentir trompé.
2. **Se prémunir contre des sanctions** : l'article 99 du règlement prévoit des amendes, mais leur montant et leur application dépendront de la gravité, de la nature de l'infraction et de l'appréciation des autorités. Le non-respect des obligations de transparence peut entraîner des sanctions jusqu'à 15 M€ ou 3 % du chiffre d'affaires mondial annuel, selon les modalités fixées par le texte. Ces chiffres sont des plafonds légaux, pas des montants systématiques.

Ce guide vous aide à faire un premier diagnostic et à prioriser vos actions.

---

## 1) Ce qui change pour une PME

### 1.1 Trois obligations concrètes à retenir

Pour une PME qui n'utilise pas d'IA à haut risque (santé, transport, recrutement automatisé, etc.), les trois obligations principales sont :

**A. Informer l'utilisateur qu'il interagit avec une IA**

Lorsqu'un chatbot, un assistant virtuel ou un système génère des réponses à destination du public, l'utilisateur doit être informé dès le début de l'interaction qu'il communique avec une machine.

Exemples concernés :
- Chatbot de support client (Intercom, Crisp, Tidio, Chatbase, etc.).
- Agent conversationnel intégré à un site WordPress, Shopify ou Webflow.
- Formulaire avec réponse automatique générée par un modèle de langage.

Ce qui est exigé : une mention claire, accessible, permanente. Une simple phrase dans les conditions générales ne suffit probablement pas.

**B. Identifier les contenus générés par IA**

Les contenus textuels, audio, image ou vidéo générés par une IA et publiés à destination du public doivent être identifiables comme tels.

Exemples concernés :
- Articles de blog rédigés entièrement par un LLM.
- Images créées par Midjourney, DALL·E, Stable Diffusion, etc.
- Vidéos générées ou modifiées par IA.

Pour les images, une mention visible (« Image générée par IA ») ou un filigrane lisible est recommandée. Pour les textes, une mention en début ou en fin d'article peut suffire.

**C. Signaler les contenus manipulés (deepfakes)**

Si vous publiez une image, une vidéo ou un audio qui ressemble à une personne réelle mais qui a été créé ou sensiblement modifié par IA, une mention explicite est requise. Cette obligation vise en priorité les deepfakes et les contenus de synthèse.

### 1.2 Ce qui ne change pas

L'AI Act ne vous oblige pas à :
- Arrêter d'utiliser l'IA.
- Obtenir un agrément ou une certification préalable pour un chatbot classique.
- Publier l'intégralité de votre code ou de vos prompts.
- Payer un service obligatoire.

Il vous demande simplement d'être transparent avec vos utilisateurs.

### 1.3 Calendrier à retenir

- **2 août 2024** : entrée en vigueur du règlement.
- **2 février 2025** : interdiction des pratiques d'IA considérées comme à risque inacceptable.
- **2 août 2026** : application des obligations de transparence de l'article 50 pour les systèmes d'IA à usage général et les chatbots.
- **2 décembre 2026** : certaines obligations techniques de marquage des contenus générés sont progressivement renforcées.

Ces dates sont celles communiquées par la Commission européenne. Elles peuvent faire l'objet de précisions ou de reports ponctuels. Il est utile de se tenir informé via les canaux officiels.

---

## 2) Suis-je concerné ?

### 2.1 Arbre de décision simple

Posez-vous ces quatre questions :

**Question 1 : Mon site ou mon application expose-t-il une interface conversationnelle au public ?**

- Oui → Vous êtes probablement concerné par l'article 50(1).
- Non → Passez à la question 2.

**Question 2 : Publions-nous du contenu généré par IA (texte, image, audio, vidéo) ?**

- Oui → Vous êtes probablement concerné par l'article 50(2).
- Non → Passez à la question 3.

**Question 3 : Le contenu généré est-il modifié ou manipulé de manière significative (deepfake, synthèse vocale, etc.) ?**

- Oui → Vous êtes concerné par l'article 50(3) et devez apposer une mention explicite.
- Non → Passez à la question 4.

**Question 4 : L'IA est-elle utilisée en interne uniquement, sans interaction avec le public ?**

- Oui → Les obligations de transparence de l'article 50 ne s'appliquent probablement pas. D'autres règles peuvent cependant s'appliquer (données personnelles, droit d'auteur, etc.).

### 2.2 Exemples de situations courantes

| Situation | Concerné ? | Action attendue |
|---|---|---|
| Chatbot Crisp sur la page contact | Oui | Mention « Vous parlez à un assistant IA » |
| Article de blog rédigé avec ChatGPT | Oui | Mention « Article rédigé avec l'aide d'une IA » |
| Image générée par Midjourney sur le site | Oui | Mention « Image générée par IA » |
| Assistant IA utilisé uniquement en interne pour rédiger des emails | Non | Former les équipes, documenter l'usage |
| Recommandation algorithmique simple (produits similaires) | Probablement non | Vérifier si le système entre dans le champ de l'article 50 |
| Recrutement automatisé par IA | Oui, avec des obligations plus strictes | Se rapprocher d'un conseil spécialisé |

### 2.3 Ce qui relève d'autres réglementations

L'AI Act ne remplace pas :
- Le RGPD, si vous traitez des données personnelles via l'IA.
- Le droit d'auteur, si vous utilisez des contenus protégés pour entraîner ou alimenter un modèle.
- Les règles sectorielles (médical, financier, etc.).

Ces sujets dépassent le cadre de ce guide. En cas de doute, consultez un professionnel compétent.

---

## 3) Les actions prioritaires

Cette liste est conçue comme un plan d'action progressif. Vous pouvez l'appliquer sans compétences techniques avancées.

### Étape 1 — Faire l'inventaire de vos systèmes d'IA

Durée estimée : 30 minutes.

Relevez tous les outils d'IA présents sur votre site, vos applications et vos processus publics :

- [ ] Chatbots et assistants conversationnels.
- [ ] Outils de génération de texte utilisés pour le contenu public.
- [ ] Outils de génération d'image, d'audio ou de vidéo.
- [ ] Outils de traduction automatique affichés publiquement.
- [ ] Systèmes de recommandation ou de personnalisation basés sur l'IA.
- [ ] Outils internes susceptibles de produire des documents envoyés à des tiers.

Pour chaque outil, notez : le nom, l'éditeur, l'usage, les pages concernées.

### Étape 2 — Vérifier les mentions de transparence existantes

Durée estimée : 1 heure.

Pour chaque système d'IA public :

- [ ] Une mention indique-t-elle clairement qu'il s'agit d'une IA ?
- [ ] Cette mention est-elle visible dès le début de l'interaction ?
- [ ] Elle est-elle accessible sur mobile ?
- [ ] Elle est-elle présente dans toutes les langues concernées ?
- [ ] Les conditions générales se contentent-elles de renvoyer au sujet ?

Une mention dans les CGV seule est généralement insuffisante. La transparence doit être contextualisée.

### Étape 3 — Rédiger les mentions manquantes

Durée estimée : 1 à 2 heures.

Exemples de mentions à adapter :

**Chatbot :**
> « Vous discutez avec un assistant automatique. Un humain peut prendre le relais si vous le souhaitez. »

**Contenu textuel généré :**
> « Cet article a été rédigé avec l'aide d'un outil d'intelligence artificielle. Il a été relu avant publication. »

**Image générée :**
> « Image générée par intelligence artificielle. »

**Deepfake ou contenu de synthèse :**
> « Cette vidéo a été créée par intelligence artificielle et ne montre pas un événement réel. »

### Étape 4 — Mettre à jour les pages concernées

Durée estimée : 1 à 3 heures selon le nombre de pages.

- [ ] Ajouter la mention dans l'interface du chatbot.
- [ ] Ajouter une légende sous chaque image générée.
- [ ] Ajouter une mention en début ou fin d'article généré.
- [ ] Publier une page « transparence IA » récapitulative.

### Étape 5 — Documenter votre démarche

Durée estimée : 30 minutes.

Tenez à jour un registre interne avec :
- la liste des systèmes d'IA utilisés ;
- les mentions mises en place ;
- les dates de mise à jour ;
- les responsables.

Ce document vous sera utile en cas de contrôle ou de question d'un client.

### Étape 6 — Prévoir un point de contrôle régulier

- [ ] Revoir l'inventaire tous les 6 mois.
- [ ] Vérifier les mentions lors de chaque refonte ou ajout d'outil.
- [ ] Se tenir informé des évolutions réglementaires.

---

## 4) Ressources et outils

### 4.1 Ressources officielles

1. **Règlement (UE) 2024/1689** — Texte officiel de l'AI Act : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689
2. **Commission européenne — AI Act** : https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
3. **Eur-Lex — Version consolidée du règlement** : https://eur-lex.europa.eu/
4. **Observatoire européen de l'IA (AI Watch)** : https://op.europa.eu/en/web/eudatathon/ai-watch
5. **Guides de mise en conformité de la Commission** : https://digital-strategy.ec.europa.eu/en/library/ai-act-commission-guidelines
6. **Parlement européen — Dossier AI Act** : https://www.europarl.europa.eu/topics/en/article/20230601STO93804/eu-ai-act-first-regulation-on-artificial-intelligence
7. **CNIL — Intelligence artificielle** : https://www.cnil.fr/fr/intelligence-artificielle
8. **CNIL — Questions/Réponses sur l'IA et la protection des données** : https://www.cnil.fr/fr/ia-generative
9. **Direction générale des entreprises (France) — AI Act** : https://www.economie.gouv.fr/entreprises/reglementation-intelligence-artificielle
10. **Service-Public.fr — Intelligence artificielle** : https://www.service-public.fr/particuliers/vosdroits/N41807
11. **Publications Office of the EU — Études sur l'IA** : https://publications.europa.eu/
12. **EDPB — Guidelines on AI and data protection** : https://edpb.europa.eu/our-work-tools/general-guidance/guidelines-artificial-intelligence_en
13. **AI Office de la Commission européenne** : https://digital-strategy.ec.europa.eu/en/activities/ai-office
14. **Shaping Europe's digital future — AI Act Q&A** : https://digital-strategy.ec.europa.eu/en/news/eu-ai-act-questions-and-answers
15. **Registre des données personnelles et IA — CNIL** : https://www.cnil.fr/fr/rgpd-de-definir-sa-feuille-de-route

### 4.2 Outils pratiques

**BadgeIA** — https://badgeia.brozapi.com  
BadgeIA est un outil technique d'aide à la transparence développé par le studio Brozapi. Il propose un scanner gratuit qui détecte les chatbots et assistants IA présents sur une page web, un widget de transparence prêt à intégrer, un étiqueteur d'images et une page registre IA publique et datée. Il ne constitue pas un conseil juridique ni une garantie de conformité, mais il peut accélérer la mise en place des mentions de transparence sur un site statique ou CMS (WordPress, Shopify, Webflow, etc.).

Autres outils à considérer :
- Les générateurs de filigrane pour images IA (outils des éditeurs de modèles ou solutions tierces).
- Les CMS avec plugins de consentement et de mentions légales.
- Les tableaux de bord de gouvernance IA proposés par certains éditeurs d'enterprise software.

---

## 5) Limites et mention honnête

### 5.1 Ce que ce guide ne couvre pas

Ce guide se concentre sur les obligations de transparence de l'article 50 pour les PME ayant un site web ou une application grand public. Il ne traite pas :
- des systèmes d'IA à haut risque (santé, justice, recrutement, éducation, etc.) ;
- des obligations spécifiques aux modèles de fondation à usage général ;
- de la conformité RGPD dans le détail ;
- des questions de propriété intellectuelle liées aux modèles génératifs ;
- des règles sectorielles ou nationales complémentaires.

### 5.2 Aucune garantie de conformité

Aucun outil, badge, scanner ou guide PDF ne peut à lui seul garantir que votre organisation respecte l'AI Act. La conformité dépend :
- de votre contexte réel ;
- des systèmes que vous utilisez ;
- de la manière dont vous informez vos utilisateurs ;
- de l'interprétation des autorités de contrôle et des juridictions compétentes.

Si votre activité repose fortement sur l'IA, ou si vous utilisez des systèmes à haut risque, faites appel à un conseil juridique ou à un cabinet spécialisé.

### 5.3 Restez vigilant sur les évolutions

Le paysage réglementaire de l'IA évolue rapidement. Les guides de la Commission européenne, les positions des autorités nationales et la jurisprudence apporteront des précisions importantes dans les mois et années à venir. Prévoyez de relire ce guide et vos pratiques au moins une fois par an.

---

## Conclusion

L'AI Act n'est pas une menace pour les PME qui utilisent l'IA de manière responsable. C'est surtout un rappel : informer les utilisateurs, être transparent sur les contenus générés, et documenter sa démarche.

Le plan d'action peut se résumer en six points :

1. Inventorier vos systèmes d'IA publics.
2. Vérifier vos mentions de transparence.
3. Rédiger les mentions manquantes.
4. Les intégrer sur votre site.
5. Documenter votre démarche.
6. Recontrôler régulièrement.

Vous pouvez réaliser la majeure partie de ces actions seul, sans budget spécifique. Si vous préférez accélérer la mise en place d'un widget de transparence ou d'une page registre, des outils comme BadgeIA peuvent vous aider. Dans tous les cas, gardez à l'esprit qu'aucun outil ne remplace une vérification humaine et, le cas échéant, un conseil juridique adapté à votre situation.

---

*Guide rédigé par Brozapi — Version 1.0 — Août 2026.*  
*Ce document est fourni à titre indicatif. Il ne constitue pas un conseil juridique.*
