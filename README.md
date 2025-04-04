# qgis-plugin

Ce plugin QGIS est destiné aux <ins> collectivités et services publics des départements de Savoie et Haute-Savoie  adhérents du GIP RGD Savoie Mont Blanc </ins>. Un login de connexion est nécessaire. Pour une demande de login adresser une demande à info@rgd.fr

Ce plugin fournit  :

+ un accès simple aux flux de données géographiques utiles en Savoie et Haute-Savoie : plan cadastral, photographies aériennes, données d'urbanisme, cartes topographiques, données alimétriques, PCRS…
+ des fonctionnalités de recherche de références cadastrales ou adresses postales
+ une fonctionnalité d'édition de rapports cadastraux (fiche descriptive de parcelle, relevé de propriété).




Code source du projet: https://github.com/rgdsmb/rgd-qgis-plugin

Ce projet est un fork (projet dérivé) du plugin du CRAIG (lui-même fork d'autres projets..):
* https://github.com/gipcraig/qgis-plugin
  
## Installation

L'installation du plugin est réalisable directement depuis QGIS via le menu Extension > Installer/Gérer les extensions. Saisir "RGD Savoie Mont Blanc Plugin" dans la barre de recherche.
Attention : la version minimum requise est la version 3.40.2 

## Utilisation

Une barre d'outil permet d'accéder aux différentes fonctionnalités du plugin:

![image](https://github.com/user-attachments/assets/c33450b1-dd5b-484f-82e3-01b3e2b8260b)
+ Affichage du panneau latéral listant les couches disponibles
+ interrogation parcellaire cadastrale
+ Recherche de parcelles / lieudit
+ Recherche d'adresses postales


### Affichage des couches de données disponibles

* Via le menu de QGIS : Extension > RGD > Afficher le panneau latéral
* Via la barre de bouton

Un nouveau panneau latéral apparaît alors. Il contient une vue arborescente des
différentes ressources proposées par la RGD ou d'autres services
fournis par d'autres producteurs de données.

![image](https://github.com/user-attachments/assets/87026218-8f76-4a89-8832-3b994b3a401b)


Pour ajouter une couche sur la carte courante de QGIS vous pouvez utiliser l'une des opérations suivantes :

* double-clic sur le nœud en question
* clic-droit sur le nœud en question et menu contextuel "Ajouter à la carte"
* glisser-déposer du nœud sur la carte de QGIS

Une fenêtre d'authnetification apparaît :

![image](https://github.com/user-attachments/assets/978b6cdb-dc34-4fbc-b293-b956f1f381bf)

Saisir vos identifiants RGD.CONNECT

Confirmer votre identité en siasissant le code de vérification reçu par mail

Le message ci-dessous apparaît à l'issue du processus d'authnetification:

![image](https://github.com/user-attachments/assets/246271f6-78c8-438b-82c2-6a1874d6f175)

Vous pouvez alors retourner sur la fenêtre de QGIS et commencer à utiliser le plugin



### Interrogation parcellaire cadastrale 

* Via le menu de QGIS : Extension > RGD > Interrogation parcellaire
* Via la barre de bouton

Puis clic sur la carte pour ouvrir la fiche descriptive de la parcelle. 

![image](https://github.com/user-attachments/assets/1fb5b5a9-4dbc-426c-b509-f423cde3b6d9)

<ins>Attention : la parcellaire doit faire partie de votre territoire de compétences ( défini par l'administarteur de la RGD au niveau du profil de votre login)</ins>

![image](https://github.com/user-attachments/assets/5af8248e-0b19-4f01-bfee-d574448a518b)

### Recherche de parcelles / lieudit

* Via le menu de QGIS : Extension > RGD > Localisation parcellaire
* Via la barre de bouton

![image](https://github.com/user-attachments/assets/18febe09-360f-419f-98d3-0395a30c1a9b)

![image](https://github.com/user-attachments/assets/ac65854e-a1a2-4924-831d-133f958cadef)



## Paramètres

Les paramètres de ce plugin sont accessibles en allant dans le menu Extensions > RGD Savoie Mont Blanc > Paramétrer le plugin :

Par défaut, le fichier de configuration de l'extension est téléchargé à chaque
lancement de QGIS, ce qui vous assure que l'arborescence soit à jour par
rapport au contenu mis à disposition par le RGD. Vous pouvez également
décider de masquer ou non les dossiers vides, ou bien les couches en cours
d'intégration.

## Auteurs originaux

Auteurs:
* Even Rouault (SPATIALYS)
* Landry Breuil (CRAIG)
* Benjamin Chartier (Région Picardie, Région Hauts-de-France, Neogeo Technologies puis en tant qu'indépendant)
* Julie Pierson (UMR LETG)

Source d'inspiration :
* Nicolas Damiens (Picardie Nature)

Autres remerciements :
* Auteurs des icônes de QGIS, reprises dans l'arbre des ressources
* Pour le fichier gipcraig/images/Icon_Simple_Warn.png cf.
https://commons.wikimedia.org/wiki/File:Icon_Simple_Warn.png


## Licence

Licence : [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html#licenseText)

cf. fichier LICENSE.txt

cf. https://choosealicense.com/licenses/bsd-3-clause/
