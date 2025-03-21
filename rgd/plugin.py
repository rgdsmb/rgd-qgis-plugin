# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QAction, QMenu, QToolBar
from qgis.PyQt.QtCore import Qt, QSettings, QUrl
from qgis.PyQt.QtGui import QIcon, QDesktopServices

from qgis.core import QgsApplication
from qgis.gui import QgsMapToolEmitPoint

import os.path

from rgd.utils.plugin_globals import PluginGlobals
from rgd.gui.dock import DockWidget
from rgd.gui.about_box import AboutBox
from rgd.gui.param_box import ParamBox
from rgd.gui.localisation_cadastrale import LocalisationCadastraleDialog
from rgd.gui.recherche_adresse import RechercheAdresseDialog
from rgd.nodes.tree_node_factory import TreeNodeFactory
from rgd.nodes.tree_node_factory import download_tree_config_file
from rgd.utils.maptools import reproject_point

class SimpleAccessPlugin:
    """
    Plugin initialisation.
    A json config file is read in order to configure the plugin GUI.
    """

    def __init__(self, iface):
        self.iface = iface
        self.dock = None

        PluginGlobals.instance().set_plugin_path(
            os.path.dirname(os.path.abspath(__file__))
        )
        PluginGlobals.instance().set_plugin_iface(self.iface)

        PluginGlobals.instance().create_oauth2_config()

        PluginGlobals.instance().reload_globals_from_qgis_settings()

        config_struct = None
        config_string = ""

        # Download the config if needed
        if self.need_download_tree_config_file():
            download_tree_config_file(PluginGlobals.instance().CONFIG_FILE_URLS[0])

        # Read the resources tree file and update the GUI
        self.ressources_tree = TreeNodeFactory(
            PluginGlobals.instance().config_file_path
        ).root_node

    def need_download_tree_config_file(self):
        """
        Do we need to download a new version of the resources tree file?
        2 possible reasons:
        - the user wants it to be downloading at plugin start up
        - the file is currently missing
        """

        return (
            PluginGlobals.instance().CONFIG_FILES_DOWNLOAD_AT_STARTUP > 0
            or not os.path.isfile(PluginGlobals.instance().config_file_path)
        )

    def initGui(self):
        """
        Plugin GUI initialisation.
        Creates a menu item in the menu of QGIS
        Creates a toolbar
        Creates a DockWidget containing the tree of resources
        """

        self.canvas = self.iface.mapCanvas()
        self.interrogTool = QgsMapToolEmitPoint(self.canvas)
        self.interrogTool.canvasClicked.connect(self.display_point)

        icon_show_panel = os.path.join(PluginGlobals.instance().images_dir_path, "volet_lateral_v1.png")
        self.show_panel_action = QAction(
            QIcon(icon_show_panel),
            u"Afficher le panneau latéral", self.iface.mainWindow()
        )
        self.show_panel_action.setCheckable(True)
        self.show_panel_action.triggered.connect(self.showPanelMenuTriggered)

        icon_path = os.path.join(PluginGlobals.instance().images_dir_path, "parcelle_info.png")
        self.interrogation_parcellaire_action = QAction(
            QIcon(icon_path), u"Interrogation parcellaire…", self.iface.mainWindow()
        )
        self.interrogation_parcellaire_action.triggered.connect(self.interrogationParcellaireTriggered)

        icon_path = os.path.join(PluginGlobals.instance().images_dir_path, "recherche_parcelle.png")
        self.localisation_cadastrale_action = QAction(
            QIcon(icon_path), u"Localisation cadastrale…", self.iface.mainWindow()
        )
        self.localisation_cadastrale_action.triggered.connect(self.localisationCadastraleTriggered)

        icon_path = os.path.join(PluginGlobals.instance().images_dir_path, "recherche_adresse.png")
        self.recherche_adresse_action = QAction(
            QIcon(icon_path), u"Recherche par adresse…", self.iface.mainWindow()
        )
        self.recherche_adresse_action.triggered.connect(self.rechercheAdresseTriggered)

        # Create a menu
        self.createPluginMenu()

        # Create a toolbar
        self.createToolbar()

        # Create a dockable panel with a tree of resources
        self.dock = DockWidget()
        self.dock.set_tree_content(self.ressources_tree)
        self.inVisibilityChanged = False
        self.dock.visibilityChanged.connect(self.dockVisibilityChanged)
        self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        s = QSettings()
        if s.value("{0}/show_dock".format(PluginGlobals.instance().PLUGIN_TAG), "1") == "1":
            self.show_panel_action.setChecked(True)
        else:
            self.dock.hide()
            self.show_panel_action.setChecked(False)

    def createPluginMenu(self):
        """
        Creates the plugin main menu
        """
        plugin_menu = self.iface.pluginMenu()
        self.plugin_menu = QMenu(PluginGlobals.instance().PLUGIN_NAME, plugin_menu)
        plugin_menu.addMenu(self.plugin_menu)

        self.plugin_menu.addAction(self.show_panel_action)

        self.plugin_menu.addAction(self.interrogation_parcellaire_action)

        self.plugin_menu.addAction(self.localisation_cadastrale_action)

        self.plugin_menu.addAction(self.recherche_adresse_action)

        icon_path = os.path.join(PluginGlobals.instance().images_dir_path, "config.png")
        param_action = QAction(QIcon(icon_path), u"Paramétrer le plugin…", self.iface.mainWindow())
        param_action.triggered.connect(self.paramMenuTriggered)
        self.plugin_menu.addAction(param_action)

        icon_path = os.path.join(PluginGlobals.instance().images_dir_path, "about.png")
        about_action = QAction(QIcon(icon_path), u"À propos…", self.iface.mainWindow())
        about_action.triggered.connect(self.aboutMenuTriggered)
        self.plugin_menu.addAction(about_action)


    def createToolbar(self):
        """ Creates a toolbar """

        self.toolbar = self.iface.mainWindow().findChild(QToolBar, PluginGlobals.instance().PLUGIN_NAME)
        if self.toolbar:
            self.toolbar.setVisible(True)
            return

        self.toolbar = QToolBar(PluginGlobals.instance().PLUGIN_NAME, self.iface.mainWindow())
        self.toolbar.setObjectName(PluginGlobals.instance().PLUGIN_NAME)
        self.iface.addToolBar(self.toolbar)
        self.toolbar.setVisible(True)

        self.toolbar.addAction(self.show_panel_action)

        self.toolbar.addAction(self.interrogation_parcellaire_action)

        self.toolbar.addAction(self.localisation_cadastrale_action)

        self.toolbar.addAction(self.recherche_adresse_action)


    def showPanelMenuTriggered(self):
        """
        Shows or hides the dock widget
        """
        if self.show_panel_action.isChecked():
            self.dock.show()
        else:
            self.dock.hide()


    def dockVisibilityChanged(self, visibility):
        if self.inVisibilityChanged:
            return
        s = QSettings()
        self.inVisibilityChanged = True
        s.setValue(u"{0}/show_dock".format(PluginGlobals.instance().PLUGIN_TAG), "1" if visibility else "0")
        self.show_panel_action.setChecked(visibility)
        self.inVisibilityChanged = False


    def aboutMenuTriggered(self):
        """
        Shows the About box
        """
        dialog = AboutBox(self.iface.mainWindow())
        dialog.exec()

    def paramMenuTriggered(self):
        """
        Shows the Param box
        """
        dialog = ParamBox(self.iface.mainWindow(), self.dock)
        dialog.exec()

    def interrogationParcellaireTriggered(self):
        self.canvas.setMapTool(self.interrogTool)

    def display_point(self, point, button):
        try:
            x = float(point.x())
            y = float(point.y())
            canvas_crs = self.canvas.mapSettings().destinationCrs()
            canvas_crs_auth_id = canvas_crs.authid()

            x, y = reproject_point(x, y, canvas_crs_auth_id, "EPSG:2154")
            url = f"https://majicad.rgd74.fr/cadastre/index.phtml?operation=GetFicheparc&type=complet&format=html&geom=SRID%3D2154%3BPOINT%28{x}%20{y}%29"
            QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            self.iface.messageBar().pushMessage('PyErreur : requete intPyErrogation parcellaire | PyErr:' + str(e), Qgis.Warning)

    def localisationCadastraleTriggered(self):
        dialog = LocalisationCadastraleDialog(self.iface.mainWindow(), self.iface, self.ressources_tree)
        dialog.exec()

    def rechercheAdresseTriggered(self):
        dialog = RechercheAdresseDialog(self.iface.mainWindow(), self.iface)
        dialog.exec()

    def unload(self):
        """
        Removes the plugin menu
        """
        self.iface.pluginMenu().removeAction(self.plugin_menu.menuAction())

        self.iface.mainWindow().removeToolBar(self.toolbar)
