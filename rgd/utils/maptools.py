from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPoint,
    QgsProject,
    QgsRectangle,
)

def reproject_point(x, y, source_crs_name, dst_crs_name):
    """
    Reproject (x, y) from source_crs_name to dst_crs_name
    """
    source_crs = QgsCoordinateReferenceSystem(source_crs_name)
    dest_crs = QgsCoordinateReferenceSystem(dst_crs_name)
    transformer = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())
    newpoint = transformer.transform(x, y)
    return newpoint.x(), newpoint.y()

def center_on_xy(plugin_iface, x, y, zoomScale):
    """
    Center on (x,y), given in map canvas CRS, using specified zoomScale
    """
    mc = plugin_iface.mapCanvas()
    mapwidth = mc.extent().xMaximum() - mc.extent().xMinimum()
    mapheight = mc.extent().yMaximum() - mc.extent().yMinimum()
    xmin = float(x) - mapwidth/2
    xmax = float(x) + mapwidth/2 
    ymin = float(y) - mapheight/2
    ymax = float(y) + mapheight/2
    rect = QgsRectangle(float(xmin),float(ymin),float(xmax),float(ymax))
    mc.setExtent(rect)
    mc.zoomScale(zoomScale)
    mc.refresh()
