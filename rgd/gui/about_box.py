# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextBrowser,
    QFrame,
)
from qgis.PyQt.QtGui import QPixmap

from rgd.utils.plugin_globals import PluginGlobals


class AboutBox(QDialog):
    """
    About box of the plugin
    """

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        mainLayout = QVBoxLayout()

        logo_file_path = PluginGlobals.instance().logo_file_path
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap(logo_file_path))
        mainLayout.addWidget(self.logo)

        title = u"À propos de l'extension " + PluginGlobals.instance().PLUGIN_TAG + "…"
        description1 = """Plugin QGIS fournissant un accès simple aux flux de données géographiques réservés aux abonnés des géoservices du  <a href="https://www.rgd.fr//">GIP RGD Savoie Mont Blanc</a> sur les départements de Savoie et de Haute-Savoie (plan cadastral, photographies aériennes, données d'urbanismes, cartes topographiques, données alimétriques, PCRS…). Fonctionnalités de recherche et consultation de données cadastrales. Recherche d'adresse postale. Veuillez noter que les services accessibles par le plugin nécessitent d'avoir un accès autorisé accordé par la RGD Savoie Mont Blanc sur le territoire de compétence de chaque utilisateur (cf. accès à la documentation littérale cadastrale). Abonnés : contactez notre support pour toute création de compte. Version {}<br>""".format(
            PluginGlobals.instance().PLUGIN_VERSION
        )
        description2 = """Plus d'informations à l'adresse suivante :<br><a href='{0}'>{0}</a><br>""".format(
            PluginGlobals.instance().PLUGIN_SOURCE_REPOSITORY
        )
        description3 = """Merci aux créateurs des plugins <a href="https://github.com/gipcraig/qgis-plugin">CRAIG</a>, <a href="https://github.com/geograndest/qgis-plugin">DataGrandEst</a>, <a href="https://github.com/geo2france/idg-qgis3-plugin">Géo2France </a>, <a href="https://github.com/geobretagne/qgis-plugin">GéoBretagne</a> et <a href="https://gitlab.in2p3.fr/letg/indigeo-for-qgis">Indigéo </a>sur lesquels ce plugin est basé !"""

        self.textArea = QTextBrowser()
        #        self.textArea.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.textArea.setOpenExternalLinks(True)
        self.textArea.setReadOnly(True)
        self.textArea.setHtml(description1)
        self.textArea.append(description2)
        self.textArea.append(description3)
        self.textArea.setFrameShape(QFrame.NoFrame)
        mainLayout.addWidget(self.textArea)

        self.setModal(True)
        self.setSizeGripEnabled(False)

        self.setLayout(mainLayout)

        self.setFixedSize(600, 320)
        self.setWindowTitle(title)
