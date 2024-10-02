# qgis-plugin
Plugin pour QGIS fournissant un accès simple aux flux de donnéesgéographiques
WMS/WMTS et WFS du RGD et d'autres ressources géographiques utiles en Savoie et
Haute-Savoie

Code source du projet: https://github.com/rgdsmb/rgd-qgis-plugin

Ce projet est un fork (projet dérivé) du plugin du CRAIG (lui-même fork d'autres projets..):
* https://github.com/gipcraig/qgis-plugin

## Utilisation

Affichage des ressources mises à disposition des utilisateurs via l'extension :
* Dans le menu de QGIS : Extension > RGD > Afficher le panneau latéral

Un nouveau panneau latéral apparaît alors. Il contient une vue arborescente des
différentes ressources proposées par le RGD, ainsi que d'autres services
fournis par d'autres producteurs de données.

Pour ajouter une couche WMS ou une classe d'entités WFS sur la carte courante de QGIS vous pouvez utiliser l'une des
opérations suivantes :
* double-clic sur le nœud en question
* clic-droit sur le nœud en question et menu contextuel "Ajouter à la carte"
* glisser-déposer du nœud sur la carte de QGIS

Il est possible de faire des recherches dans la liste des couches avec la barre
de recherche placée au dessus de l'arborescence.

Plus de détails sur une couche sont affichés en laissant la souris une seconde
sur le titre d'une couche.

Pour consulter les métadonnées associées à une couche : clic droit sur la
couche puis "Afficher les métadonnées".

Si vous avez fermé le panneau RGD et que vous voulez l'afficher à nouveau, 2 possibilités :

* menu Extensions, RGD, Afficher le panneau latéral
* menu Vue, Panneaux, cocher RGD

## Paramètres

Les paramètres de ce plugin sont accessibles en allant dans le menu Extensions > RGD > Paramétrer le plugin :

Par défaut, le fichier de configuration de l'extension est téléchargé à chaque
lancement de QGIS, ce qui vous assure que l'arborescence soit à jour par
rapport au contenu mis à disposition par le RGD. Vous pouvez également
décider de masquer ou non les dossiers vides, ou bien les couches en cours
d'intégration.

## Auteurs originaux

Auteurs:
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
