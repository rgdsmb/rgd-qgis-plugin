import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
)
from qgis.PyQt.QtCore import QObject, QEvent, QSettings, Qt, QTimer, QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsMessageLog,
    QgsNetworkAccessManager,
)

from rgd.utils.maptools import reproject_point, center_on_xy
from rgd.utils.network_utils import get_json_response
from rgd.utils.plugin_globals import PluginGlobals
from rgd.utils.temp_map_layer_with_red_cross import TempMapLayerWithRedCross

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'recherche_adresse.ui'))


class RechercheAdresseDialog(QDialog, FORM_CLASS):

    IDX_LABEL = 0
    IDX_LONGITUDE = 1
    IDX_LATITUDE = 2

    def __init__(self, parent, plugin_iface):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.plugin_iface = plugin_iface
        self.temp_layer = None

        # gestion de la pos fenetre
        self.userPos = None
        s = QSettings()
        y = s.value("qgis_rgd_plugin/adresse_ywin")
        x = s.value("qgis_rgd_plugin/adresse_xwin")
        if not (x is None):
            y = int(y)
            x = int(x)
            self.move(x,y)

        self.rechercherButton.clicked.connect(
            self.rechercherButton_clicked
        )

        self.button_box.button(QDialogButtonBox.Close).clicked.connect(
            self.close_button_clicked
        )

        self.rechercherButton.setEnabled(False)
        self.adresse.textChanged.connect(self.updateRechercheButtonState)

        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Adresse complète", "Longitude", "Latitude"])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.cellDoubleClicked.connect(self.cellDoubleClicked_triggered)

        self.btnsearch.clicked.connect(self.btnsearch_clicked)

        # Make window non-modal in practice
        self.show()
        self.resizeTableColumns()

        self.reply = None

    def close_button_clicked(self):
        """ """
        self.close()

    def abortQueries(self):
        if self.reply:
            self.reply.abort()
            self.reply = None

    def cleanup(self):
        # enregistrement position fenetre
        s = QSettings()
        s.setValue("qgis_rgd_plugin/adresse_ywin", self.pos().y())
        s.setValue("qgis_rgd_plugin/adresse_xwin", self.pos().x())

        self.abortQueries()
        QApplication.restoreOverrideCursor()

        if self.temp_layer:
            self.temp_layer.close()
            self.temp_layer = None

    def closeEvent(self, event):
        self.cleanup()

    def reject(self):
        self.cleanup()
        super(RechercheAdresseDialog, self).reject()

    def resizeEvent(self, event):
        super().resizeEvent(event)  # Call the base class resize event
        self.resizeTableColumns()

    def resizeTableColumns(self):
        total_width = self.tableWidget.viewport().width()  # Total available width of the table
        self.tableWidget.setColumnWidth(0, total_width // 2)  # 50% for the first column
        self.tableWidget.setColumnWidth(1, total_width // 4)  # 25% for the second column
        self.tableWidget.setColumnWidth(2, total_width // 4)  # 25% for the third column


    def updateRechercheButtonState(self, newText):
        if self.adresse.text():
            self.rechercherButton.setEnabled(True)
        else:
            self.rechercherButton.setEnabled(False)

    def rechercherButton_clicked(self):
        query = QUrlQuery()
        q = self.adresse.text()
        if len(q) < 3 or len(q) > 200:
            # Harcoding server constraint to get error message in French
            box = QMessageBox(QMessageBox.Icon.Warning, "Erreur lors de la requête",
                              "La requête doit comprendre entre 3 et 200 caractères, le premier étant un chiffre ou une lettre")
            box.exec()
            return
        query.addQueryItem("q", q)
        # Prioritize results on 73/74 departments
        query.addQueryItem("lat", "45.76")
        query.addQueryItem("lon", "6.38")
        url = QUrl("https://api-adresse.data.gouv.fr/search/")
        url.setQuery(query)
        req = QNetworkRequest(url)
        self.reply = QgsNetworkAccessManager.instance().get(req)
        self.reply.finished.connect(self.requestFinished)

    def requestFinished(self):
        reply = self.sender()
        self.reply = None
        response = get_json_response(reply)
        if not response:
            return
        self.tableWidget.clearContents()
        row = 0
        for feature in response["features"]:
            geometry = feature["geometry"]
            if geometry["type"] == "Point" and "properties" in feature and "label" in feature["properties"] and "coordinates" in geometry:
                row += 1

        self.tableWidget.setRowCount(row)

        row = 0
        for feature in response["features"]:
            geometry = feature["geometry"]
            if geometry["type"] == "Point" and "properties" in feature and "label" in feature["properties"] and "coordinates" in geometry:
                item = QTableWidgetItem(str(feature["properties"]["label"]))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
                self.tableWidget.setItem(row, RechercheAdresseDialog.IDX_LABEL, item)
                item = QTableWidgetItem(str(geometry["coordinates"][0]))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
                self.tableWidget.setItem(row, RechercheAdresseDialog.IDX_LONGITUDE, item)
                item = QTableWidgetItem(str(geometry["coordinates"][1]))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
                self.tableWidget.setItem(row, RechercheAdresseDialog.IDX_LATITUDE, item)
                row += 1

    def btnsearch_clicked(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row < 0:
            return
        self.center_on_coords_at_row(selected_row)

    def cellDoubleClicked_triggered(self, row, column):
        self.center_on_coords_at_row(row)

    def center_on_coords_at_row(self, row):
        longitude = float(self.tableWidget.item(row, RechercheAdresseDialog.IDX_LONGITUDE).text())
        latitude = float(self.tableWidget.item(row, RechercheAdresseDialog.IDX_LATITUDE).text())

        c = self.plugin_iface.mapCanvas()
        crs = c.mapSettings().destinationCrs()
        project_epsg = crs.authid()
        zoomScale = 2500

        x, y = reproject_point(longitude, latitude, "EPSG:4326", project_epsg)
        if x:
            if self.scalecheck.isChecked():
                zoomScale = self.plugin_iface.mapCanvas().scale()
            center_on_xy(self.plugin_iface, x, y, zoomScale)

        if self.temp_layer is None:
            self.temp_layer = TempMapLayerWithRedCross(self.plugin_iface, "Résultat de la recherche par adresse", 4326)
        self.temp_layer.set_marker(longitude, latitude)
