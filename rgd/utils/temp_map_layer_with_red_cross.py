from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsSymbol, QgsSimpleMarkerSymbolLayer
from qgis.PyQt.QtGui import QColor

class TempMapLayerWithRedCross:

    def __init__(self, plugin_iface, layer_name, epsg_code):

        self.plugin_iface = plugin_iface
        self.temp_layer = QgsVectorLayer(f"Point?crs=EPSG:{epsg_code}", layer_name, "memory")
        self.added_to_project = False

        # Create a red cross marker symbol
        symbol = QgsSymbol.defaultSymbol(self.temp_layer.geometryType())
        symbol_layer = QgsSimpleMarkerSymbolLayer()
        symbol_layer.setShape(QgsSimpleMarkerSymbolLayer.Cross)
        symbol_layer.setSize(5)
        symbol_layer.setStrokeWidth(2) 
        symbol_layer.setColor(QColor("red"))

        symbol.changeSymbolLayer(0, symbol_layer)

        self.temp_layer.renderer().setSymbol(symbol)

    def __del__(self):
        self.close()

    def close(self):
        if self.temp_layer:
            QgsProject.instance().removeMapLayer(self.temp_layer)
            self.temp_layer = None
            self.plugin_iface.mapCanvas().refresh()

    def set_marker(self, x, y):

        if not self.added_to_project:
            # Add the layer to the project
            QgsProject.instance().addMapLayer(self.temp_layer)
            self.added_to_project = True
        else:
            self.temp_layer.startEditing()
            feature_ids = [feature.id() for feature in self.temp_layer.getFeatures()]
            self.temp_layer.deleteFeatures(feature_ids)
            self.temp_layer.commitChanges()

        # Create a feature with the given coordinates
        point_feature = QgsFeature()
        point_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
        layer_provider = self.temp_layer.dataProvider()
        layer_provider.addFeature(point_feature)
        self.temp_layer.updateExtents()
