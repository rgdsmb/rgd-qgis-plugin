import json
import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QApplication, QDialog, QDialogButtonBox, QMessageBox
from qgis.PyQt.QtCore import QSettings, Qt, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsAuthManager,
    QgsGeometry,
    QgsMessageLog,
    QgsNetworkAccessManager,
    QgsProject,
)

from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsPointXY, QgsSymbol, QgsSimpleMarkerSymbolLayer
from qgis.PyQt.QtGui import QColor

from rgd.utils.maptools import reproject_point, center_on_xy
from rgd.utils.network_utils import get_json_response
from rgd.utils.plugin_globals import PluginGlobals

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'localisation_cadastrale.ui'))


class LocalisationCadastraleDialog(QDialog, FORM_CLASS):
    def __init__(self, parent, plugin_iface, ressources_tree):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.plugin_iface = plugin_iface
        self.ressources_tree = ressources_tree

        self.addPlanCadastralLayerIfNeeded(ressources_tree)

        # gestion de la pos fenetre
        self.userPos = None
        s = QSettings()
        y = s.value("qgis_rgd_plugin/search_ywin")
        x = s.value("qgis_rgd_plugin/search_xwin")
        if not (x is None):
            y = int(y)
            x = int(x)
            self.move(x,y)

        self.background_queries_count = 0

        self.liste_sections_reply = None
        self.liste_parcelles_reply = None
        self.liste_lieudits_reply = None
        self.map_parcelle = {}
        self.map_lieudit = {}

        self.temp_layer = None

        self.combocommunes.currentIndexChanged.connect(self.combocommunes_index_changed)
        self.combosection.currentIndexChanged.connect(self.combosection_index_changed)

        self.btnsearch.clicked.connect(self.btnsearch_clicked)

        self.button_box.button(QDialogButtonBox.Close).clicked.connect(
            self.close_button_clicked
        )
        self.update_list_communes()

        # Make window non-modal in practice
        self.show()

    def close_button_clicked(self):
        """ """
        self.close()

    def addPlanCadastralLayerIfNeeded(self, ressources_tree):

        # Check if "Plan Cadastral" layer is already displayed
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.name() == "Plan cadastral":
                return

        for child in ressources_tree.children:
            if child.title == "Plan cadastral":
                for subchild in child.children:
                    if subchild.title == "Plan cadastral":
                        subchild.run_add_to_map_action()


    def startQuery(self):
        if self.background_queries_count == 0:
            QApplication.setOverrideCursor(Qt.WaitCursor)
        self.background_queries_count += 1

    def stopQuery(self):
        self.background_queries_count -= 1
        if self.background_queries_count == 0:
            QApplication.restoreOverrideCursor()

    def abortQueries(self):
        if self.liste_sections_reply:
            self.liste_sections_reply.abort()
            self.liste_sections_reply = None
        if self.liste_parcelles_reply:
            self.liste_parcelles_reply.abort()
            self.liste_parcelles_reply = None
        if self.liste_lieudits_reply:
            self.liste_lieudits_reply.abort()
            self.liste_lieudits_reply = None

    def moveEvent(self,event):
        # enregistrement nouvelle position fenetre
        self.userPos = event.pos()

    def cleanup(self):
        # enregistrement position fenetre
        s = QSettings()
        s.setValue("qgis_rgd_plugin/search_ywin", self.pos().y())
        s.setValue("qgis_rgd_plugin/search_xwin", self.pos().x())

        self.abortQueries()
        QApplication.restoreOverrideCursor()

        if self.temp_layer:
            QgsProject.instance().removeMapLayer(self.temp_layer)
            self.plugin_iface.mapCanvas().refresh()

    def closeEvent(self, event):
        self.cleanup()

    def reject(self):
        self.cleanup()
        super(LocalisationCadastraleDialog, self).reject()

    def checkDataInResponse(self, response):
        if response is None:
            return False
        if "data" not in response:
            box = QMessageBox(QMessageBox.Warning, "Erreur lors de la requête",
                              "La réponse du serveur n'est pas au format attendu: " + json.dumps(response))
            box.exec_()
            return False
        return True

    def update_list_communes(self):
        req = QNetworkRequest(QUrl(PluginGlobals.instance().LOCALISATION_CADASTRALE_URL))
        authId = PluginGlobals.instance().AUTH_CONFIG_ID
        QgsApplication.authManager().updateNetworkRequest(req, authId)
        req.setRawHeader(b"X-Vmap-Ressource", b"cadastre/communes")
        req.setRawHeader(b"X-Vmap-Query", b"attributs=id_com|nom&order_by=id_com")
        liste_communes_reply = QgsNetworkAccessManager.instance().get(req)
        liste_communes_reply.finished.connect(self.listeCommunesRequestFinished)
        self.startQuery()

    def listeCommunesRequestFinished(self):
        self.stopQuery()
        reply = self.sender()
        response = get_json_response(reply)
        if not self.checkDataInResponse(response):
            return
        lst = []
        self.map_commune_name_to_id = {}
        for commune in response["data"]:
            lst.append(commune["nom"])
            self.map_commune_name_to_id[commune["nom"]] = commune["id_com"]
        self.combocommunes.addItems(sorted(lst))

    def combocommunes_index_changed(self):
        self.update_list_sections()
        self.update_list_lieudits()

    def update_list_sections(self):
        commune = self.combocommunes.currentText()
        req = QNetworkRequest(QUrl(PluginGlobals.instance().LOCALISATION_CADASTRALE_URL))
        authId = PluginGlobals.instance().AUTH_CONFIG_ID
        QgsApplication.authManager().updateNetworkRequest(req, authId)
        req.setRawHeader(b"X-Vmap-Ressource", b"cadastre/sections")
        id_com = self.map_commune_name_to_id[commune]
        query = """attributs=id_com|pre|section|id_sec&order_by=pre&filter={"column":"id_com","compare_operator":"=","value":"%s"}""" % id_com
        # print(query)
        req.setRawHeader(b"X-Vmap-Query", query.encode("utf-8"))
        if self.liste_sections_reply:
            self.liste_sections_reply.abort()
        if self.liste_parcelles_reply:
            self.liste_parcelles_reply.abort()
            self.liste_parcelles_reply = None
        self.liste_sections_reply = QgsNetworkAccessManager.instance().get(req)
        self.liste_sections_reply.finished.connect(self.listeSectionsRequestFinished)
        self.startQuery()

    def listeSectionsRequestFinished(self):
        self.stopQuery()
        reply = self.sender()
        if reply != self.liste_sections_reply:
            return
        response = get_json_response(reply)
        if not self.checkDataInResponse(response):
            return

        self.map_section_to_id = {}
        lst = []
        map_section_name = {}
        for section in response["data"]:
            section_name = section["section"]
            if section_name not in map_section_name:
                map_section_name[section_name] = 1
            else:
                map_section_name[section_name] += 1
        for section in response["data"]:
            section_name = section["section"]
            if "pre" in section and map_section_name[section_name] > 1:
                section_name += " (" + section["pre"] + ")"
            lst.append(section_name)
            self.map_section_to_id[section_name] = section["id_sec"]

        self.combosection.blockSignals(True)
        self.combosection.clear()
        self.combosection.blockSignals(False)
        self.combosection.addItems(sorted(lst))

    def combosection_index_changed(self):
        self.update_list_parcelles()

    def update_list_parcelles(self):
        commune = self.combocommunes.currentText()
        section = self.combosection.currentText()
        if not commune or not section:
            return

        req = QNetworkRequest(QUrl(PluginGlobals.instance().LOCALISATION_CADASTRALE_URL))
        authId = PluginGlobals.instance().AUTH_CONFIG_ID
        QgsApplication.authManager().updateNetworkRequest(req, authId)
        req.setRawHeader(b"X-Vmap-Ressource", b"cadastre/parcelles")
        id_com = self.map_commune_name_to_id[commune]
        id_section = self.map_section_to_id[section]
        query = """attributs=geom|id_com|pre|section|id_par|parcelle&order_by=pre&filter={"relation":"AND","operators":[{"column":"id_com","compare_operator":"=","value":"%s"},{"column":"id_sec","compare_operator":"=","value":"%s"}]}""" % (id_com, id_section)
        # print(query)
        req.setRawHeader(b"X-Vmap-Query", query.encode("utf-8"))
        if self.liste_parcelles_reply:
            self.liste_parcelles_reply.abort()
        self.section_for_list_parcelles = section
        self.liste_parcelles_reply = QgsNetworkAccessManager.instance().get(req)
        self.liste_parcelles_reply.finished.connect(self.listeParcellesRequestFinished)
        self.startQuery()

    def listeParcellesRequestFinished(self):
        self.stopQuery()
        reply = self.sender()
        if reply != self.liste_parcelles_reply:
            return
        response = get_json_response(reply)
        if not self.checkDataInResponse(response):
            return

        self.map_parcelle = {}
        lst = []
        map_parcelle_name = {}
        for parcelle in response["data"]:
            parcelle_name = parcelle["parcelle"]
            if parcelle_name not in map_parcelle_name:
                map_parcelle_name[parcelle_name] = 1
            else:
                map_parcelle_name[parcelle_name] += 1
        for parcelle in response["data"]:
            parcelle_name = parcelle["parcelle"]
            if "pre" in parcelle and map_parcelle_name[parcelle_name] > 1:
                parcelle_name += " (" + parcelle["pre"] + ")"
            lst.append(parcelle_name)
            self.map_parcelle[parcelle_name] = parcelle

        self.combonumero.blockSignals(True)
        self.combonumero.clear()
        self.combonumero.blockSignals(False)
        self.combonumero.addItems(sorted(lst))

    def update_list_lieudits(self):
        commune = self.combocommunes.currentText()
        req = QNetworkRequest(QUrl(PluginGlobals.instance().LOCALISATION_CADASTRALE_URL))
        authId = PluginGlobals.instance().AUTH_CONFIG_ID
        QgsApplication.authManager().updateNetworkRequest(req, authId)
        req.setRawHeader(b"X-Vmap-Ressource", b"cadastre/lieudits")
        id_com = self.map_commune_name_to_id[commune]
        query = """attributs=id|pre|tex|geom&order_by=pre|tex&filter={"column":"id_com","compare_operator":"=","value":"%s"}""" % id_com
        # print(query)
        req.setRawHeader(b"X-Vmap-Query", query.encode("utf-8"))
        if self.liste_lieudits_reply:
            self.liste_lieudits_reply.abort()
        self.liste_lieudits_reply = QgsNetworkAccessManager.instance().get(req)
        self.liste_lieudits_reply.finished.connect(self.listeLieuditsRequestFinished)
        self.startQuery()

    def listeLieuditsRequestFinished(self):
        self.stopQuery()
        reply = self.sender()
        if reply != self.liste_lieudits_reply:
            return
        response = get_json_response(reply)
        if not self.checkDataInResponse(response):
            return

        self.map_lieudit = {}
        lst = []

        map_lieudit_name = {}
        map_lieudit_name_cur = {}
        for lieudit in response["data"]:
            lieudit_name = lieudit["tex"].strip()
            if lieudit_name not in map_lieudit_name:
                map_lieudit_name[lieudit_name] = 1
            else:
                map_lieudit_name[lieudit_name] += 1
            map_lieudit_name_cur[lieudit_name] = 1

        for lieudit in response["data"]:
            lieudit_name = lieudit["tex"].strip()
            if map_lieudit_name[lieudit_name] > 1:
                counter = map_lieudit_name_cur[lieudit_name]
                map_lieudit_name_cur[lieudit_name] += 1
                lieudit_name += " (" + str(counter) + ")"

            lst.append(lieudit_name)
            self.map_lieudit[lieudit_name] = lieudit

        self.combolieudit.blockSignals(True)
        self.combolieudit.clear()
        self.combolieudit.blockSignals(False)
        self.combolieudit.addItems(sorted(lst))

    def btnsearch_clicked(self):
        if self.tabWidget.currentIndex() == 0:
            parcelle = self.combonumero.currentText()
            if not parcelle:
                return
            geom = self.map_parcelle[parcelle]['geom']
            zoomscale_parcelle = 250
            zoomScale = zoomscale_parcelle
        else:
            lieudit = self.combolieudit.currentText()
            if not lieudit:
                return
            geom = self.map_lieudit[lieudit]['geom']
            zoomscale_lieudit = 2500
            zoomScale = zoomscale_lieudit

        srid = int(geom[len("SRID="):geom.find(';')])
        wkt = geom[geom.find(';') + 1:]
        # print(srid, wkt)

        geom = QgsGeometry.fromWkt(wkt)
        centroid = geom.centroid().asPoint()
        x = centroid.x()
        y = centroid.y()

        c = self.plugin_iface.mapCanvas()
        crs = c.mapSettings().destinationCrs()
        project_epsg = crs.authid()

        x_ori, y_ori = x, y
        x, y = reproject_point(x, y, "EPSG:" + str(srid), project_epsg)
        if x:
            if self.scalecheck.isChecked():
                zoomScale = self.plugin_iface.mapCanvas().scale()
            center_on_xy(self.plugin_iface, x, y, zoomScale)

        if self.temp_layer is None:

            self.temp_layer = QgsVectorLayer(f"Point?crs=EPSG:{srid}", "Résultat de la localisation cadastrale", "memory")

            # Create a red cross marker symbol
            symbol = QgsSymbol.defaultSymbol(self.temp_layer.geometryType())
            symbol_layer = QgsSimpleMarkerSymbolLayer()
            symbol_layer.setShape(QgsSimpleMarkerSymbolLayer.Cross)
            symbol_layer.setSize(5)
            symbol_layer.setStrokeWidth(2) 
            symbol_layer.setColor(QColor("red"))

            symbol.changeSymbolLayer(0, symbol_layer)

            self.temp_layer.renderer().setSymbol(symbol)

            # Add the layer to the project
            QgsProject.instance().addMapLayer(self.temp_layer)
        else:
            self.temp_layer.startEditing()
            feature_ids = [feature.id() for feature in self.temp_layer.getFeatures()]
            self.temp_layer.deleteFeatures(feature_ids)
            self.temp_layer.commitChanges()

        # Create a feature with the given coordinates
        point_feature = QgsFeature()
        point_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x_ori, y_ori)))
        layer_provider = self.temp_layer.dataProvider()
        layer_provider.addFeature(point_feature)
        self.temp_layer.updateExtents()
