# -*- coding: utf-8 -*-

import os

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.core import (
    QgsProject,
)

from rgd.utils.plugin_globals import PluginGlobals
from rgd.utils.plugin_icons import PluginIcons

def AuthMissing():
    box = QMessageBox(QMessageBox.Warning,
                      "Authentification absente",
                      "Cette couche nécessite des éléments d'authentification. Merci de les renseigner dans la configuration du greffon")
    box.exec_()
    return None

def InvalidLayer():
    box = QMessageBox(QMessageBox.Warning,
                      "Couche invalide",
                      "Cette couche n'a pas être ajoutée. Vous ne disposez peut être pas des droits permettant d'y accéder.")
    box.exec_()
    return None


class FavoritesTreeNode:
    """ """

    def __init__(
        self,
        title,
        node_type=PluginGlobals.instance().NODE_TYPE_FOLDER,
        description=None,
        status=None,
        metadata_url=None,
        ident=None,
        params=None,
        bounding_boxes=None,
        parent_node=None,
    ):
        """ """

        self.parent_node = parent_node
        self.node_type = node_type
        self.title = title
        self.description = description
        self.status = status
        self.metadata_url = metadata_url
        self.ident = ident
        self.bounding_boxes = bounding_boxes
        self.children = []
        self.can_be_added_to_map = False
        self.icon = None

    def layer_mime_data(self):
        """
        Return the mime data used by the drag and drop process
        and needed by QGIS to add the right layer to the map
        """

        qgis_layer_details = self.get_qgis_layer_details()
        mime_data = ":".join(
            [
                qgis_layer_details["type"],
                qgis_layer_details["provider"],
                qgis_layer_details["title"].replace(":", "\\:"),
                qgis_layer_details["uri"].replace(":", "\\:"),
            ]
        )

        return mime_data

    def run_add_to_map_action(self):
        """ """

        pass

    def run_show_metadata_action(self):
        """
        Opens in the default user web browser the web page displaying the resource metadata
        """

        import webbrowser

        if self.metadata_url:
            webbrowser.open_new_tab(self.metadata_url)

    def run_report_issue_action(self):
        """
        Opens the default mail client to let the user send an issue report by email
        """

        # import webbrowser
        # webbrowser.open('mailto:')
        pass


# Subclasses of FavoritesTreeNode


class FolderTreeNode(FavoritesTreeNode):
    """
    Tree node for a folder containing other nodes
    """

    def __init__(
        self,
        title,
        node_type=PluginGlobals.instance().NODE_TYPE_FOLDER,
        description=None,
        status=None,
        metadata_url=None,
        ident=None,
        params=None,
        bounding_boxes=None,
        parent_node=None,
    ):
        """ """

        FavoritesTreeNode.__init__(
            self,
            title,
            node_type,
            description,
            status,
            metadata_url,
            ident,
            params,
            bounding_boxes,
            parent_node,
        )

        # Icon
        plugin_icons = PluginIcons.instance()
        self.icon = plugin_icons.folder_icon
        if self.status == PluginGlobals.instance().NODE_STATUS_WARN:
            self.icon = plugin_icons.warn_icon


class WmsLayerTreeNode(FavoritesTreeNode):
    """
    Tree node for a WMS layer
    """

    def __init__(
        self,
        title,
        node_type=PluginGlobals.instance().NODE_TYPE_WMS_LAYER,
        description=None,
        status=None,
        metadata_url=None,
        ident=None,
        params=None,
        bounding_boxes=None,
        requires_auth=False,
        parent_node=None,
    ):
        """ """
        FavoritesTreeNode.__init__(
            self,
            title,
            node_type,
            description,
            status,
            metadata_url,
            ident,
            params,
            bounding_boxes,
            parent_node,
        )

        self.service_url = params.get("url")
        self.layer_name = params.get("name")
        self.layer_format = params.get("format")
        self.layer_srs = params.get("srs")
        self.layer_style_name = params.get("style", "")
        self.can_be_added_to_map = True
        self.requires_auth = requires_auth

        # Icon
        plugin_icons = PluginIcons.instance()
        self.icon = plugin_icons.wms_layer_icon
        if self.status == PluginGlobals.instance().NODE_STATUS_WARN:
            self.icon = plugin_icons.warn_icon

    def get_qgis_layer_details(self):
        """
        Return the details of the layer used by QGIS to add the layer to the map.
        This dictionary is used by the run_add_to_map_action and layerMimeData methods.
        """
        url = self.service_url
        url = str(QUrl.toPercentEncoding(url), "utf-8")
        uri = u"crs={}&featureCount=10&format={}&layers={}&maxHeight=256&maxWidth=256&styles={}&url={}".format(
            self.layer_srs,
            self.layer_format,
            self.layer_name,
            self.layer_style_name,
            url,
        )
        if self.requires_auth:
            authId = PluginGlobals.instance().AUTH_CONFIG_ID
            if not authId:
                return AuthMissing()
            uri = "authcfg=" + authId + "&" + uri

        qgis_layer_uri_details = {
            "type": "raster",
            "provider": "wms",
            "title": self.title,
            "uri": uri,
        }

        return qgis_layer_uri_details

    def run_add_to_map_action(self):
        """
        Add the WMS layer with the specified style to the map
        """
        qgis_layer_details = self.get_qgis_layer_details()
        if qgis_layer_details is not None:
            layer = PluginGlobals.instance().iface.addRasterLayer(
                qgis_layer_details["uri"],
                qgis_layer_details["title"],
                qgis_layer_details["provider"],
            )
            if not layer or not layer.isValid():
                if layer:
                    QgsProject.instance().removeMapLayer(layer.id())
                InvalidLayer()


class WmsStyleLayerTreeNode(FavoritesTreeNode):
    """
    Tree node for a WMS layer with a specific style
    """

    def __init__(
        self,
        title,
        node_type=PluginGlobals.instance().NODE_TYPE_WMS_LAYER_STYLE,
        description=None,
        status=None,
        metadata_url=None,
        ident=None,
        params=None,
        bounding_boxes=None,
        requires_auth=False,
        parent_node=None,
    ):
        """ """

        FavoritesTreeNode.__init__(
            self,
            title,
            node_type,
            description,
            status,
            metadata_url,
            ident,
            params,
            bounding_boxes,
            parent_node,
        )

        self.layer_style_name = params.get("name")
        self.can_be_added_to_map = True

        # Icon
        plugin_icons = PluginIcons.instance()
        self.icon = plugin_icons.wms_style_icon
        if self.status == PluginGlobals.instance().NODE_STATUS_WARN:
            self.icon = plugin_icons.warn_icon

    def get_qgis_layer_details(self):
        """
        Return the details of the layer used by QGIS to add the layer to the map.
        This dictionary is used by the run_add_to_map_action and layerMimeData methods.
        """
        if self.parent_node is None:
            return None
        uri = u"crs={}&featureCount=10&format={}&layers={}&maxHeight=256&maxWidth=256&styles={}&url={}".format(
            self.parent_node.layer_srs,
            self.parent_node.layer_format,
            self.parent_node.layer_name,
            self.layer_style_name,
            self.parent_node.service_url,
        )
        if self.requires_auth:
            authId = PluginGlobals.instance().AUTH_CONFIG_ID
            if not authId:
                return AuthMissing()
            uri = "authcfg=" + authId + "&" + uri

        qgis_layer_uri_details = {
            "type": "raster",
            "provider": "wms",
            "title": self.title,
            "uri": uri,
        }

        return qgis_layer_uri_details

    def run_add_to_map_action(self):
        """
        Add the WMS layer with the specified style to the map
        """

        qgis_layer_details = self.get_qgis_layer_details()
        if qgis_layer_details is not None:
            layer = PluginGlobals.instance().iface.addRasterLayer(
                qgis_layer_details["uri"],
                qgis_layer_details["title"],
                qgis_layer_details["provider"],
            )
            if not layer or not layer.isValid():
                if layer:
                    QgsProject.instance().removeMapLayer(layer.id())
                InvalidLayer()


class WmtsLayerTreeNode(FavoritesTreeNode):
    """
    Tree node for a WMTS layer
    """

    def __init__(
        self,
        title,
        node_type=PluginGlobals.instance().NODE_TYPE_WMTS_LAYER,
        description=None,
        status=None,
        metadata_url=None,
        ident=None,
        params=None,
        bounding_boxes=None,
        requires_auth=False,
        parent_node=None,
    ):
        """ """
        FavoritesTreeNode.__init__(
            self,
            title,
            node_type,
            description,
            status,
            metadata_url,
            ident,
            params,
            bounding_boxes,
            parent_node,
        )

        self.service_url = params.get("url")
        self.layer_tilematrixset_name = params.get("tilematrixset_name")
        self.layer_name = params.get("name")
        self.layer_format = params.get("format")
        self.layer_srs = params.get("srs")
        self.layer_style_name = params.get("style", "")
        self.can_be_added_to_map = True
        self.requires_auth = requires_auth

        # Icon
        plugin_icons = PluginIcons.instance()
        self.icon = plugin_icons.wms_style_icon
        if self.status == PluginGlobals.instance().NODE_STATUS_WARN:
            self.icon = plugin_icons.warn_icon

    def get_qgis_layer_details(self):
        """
        Return the details of the layer used by QGIS to add the layer to the map.
        This dictionary is used by the run_add_to_map_action and layerMimeData methods.
        """
        url = self.service_url
        url = str(QUrl.toPercentEncoding(url), "utf-8")
        uri = u"tileMatrixSet={}&crs={}&featureCount=10&format={}&layers={}&styles={}&url={}".format(
            self.layer_tilematrixset_name,
            self.layer_srs,
            self.layer_format,
            self.layer_name,
            self.layer_style_name,
            url,
        )

        if self.requires_auth:
            authId = PluginGlobals.instance().AUTH_CONFIG_ID
            if not authId:
                return AuthMissing()
            uri = "authcfg=" + authId + "&" + uri

        qgis_layer_uri_details = {
            "type": "raster",
            "provider": "wms",
            "title": self.title,
            "uri": uri,
        }

        return qgis_layer_uri_details

    def run_add_to_map_action(self):
        """
        Add the WMTS layer to the map
        """
        qgis_layer_details = self.get_qgis_layer_details()
        if qgis_layer_details is not None:
            layer = PluginGlobals.instance().iface.addRasterLayer(
                qgis_layer_details["uri"],
                qgis_layer_details["title"],
                qgis_layer_details["provider"],
            )
            if not layer or not layer.isValid():
                if layer:
                    QgsProject.instance().removeMapLayer(layer.id())
                InvalidLayer()


class WfsFeatureTypeTreeNode(FavoritesTreeNode):
    """
    Tree node for a WFS feature type
    """

    def __init__(
        self,
        title,
        node_type=PluginGlobals.instance().NODE_TYPE_WFS_FEATURE_TYPE,
        description=None,
        status=None,
        metadata_url=None,
        ident=None,
        params=None,
        bounding_boxes=None,
        requires_auth=False,
        parent_node=None,
    ):
        """ """
        FavoritesTreeNode.__init__(
            self,
            title,
            node_type,
            description,
            status,
            metadata_url,
            ident,
            params,
            bounding_boxes,
            parent_node,
        )

        self.service_url = params.get("url")
        self.feature_type_name = params.get("name")
        self.filter = params.get("filter")
        self.wfs_version = params.get("version", "auto")
        self.layer_srs = params.get("srs")
        self.geometryTypeFilter = params.get("geometryTypeFilter")
        self.can_be_added_to_map = True
        self.requires_auth = requires_auth

        # Icon
        plugin_icons = PluginIcons.instance()
        self.icon = plugin_icons.wfs_layer_icon
        if self.status == PluginGlobals.instance().NODE_STATUS_WARN:
            self.icon = plugin_icons.warn_icon

    def get_qgis_layer_details(self):
        """
        Return the details of the layer used by QGIS to add the layer to the map.
        This dictionary is used by the run_add_to_map_action and layerMimeData methods.
        """

        uri = u"restrictToRequestBBOX='1' srsname='{}' typename='{}' version='{}' url='{}'".format(
            self.layer_srs,
            self.feature_type_name,
            self.wfs_version,
            self.service_url,
        )

        if self.geometryTypeFilter:
            uri += " geometryTypeFilter='{}'".format(self.geometryTypeFilter)

        if self.requires_auth:
            authId = PluginGlobals.instance().AUTH_CONFIG_ID
            if not authId:
                return AuthMissing()
            uri = "authcfg=" + authId + " " + uri

        if self.filter:
            uri += " filter={}".format(self.filter)

        qgis_layer_uri_details = {
            "type": "vector",
            "provider": "WFS",
            "title": self.title,
            "uri": uri,
        }

        return qgis_layer_uri_details

    def run_add_to_map_action(self):
        """
        Add the WFS feature type to the map
        """
        qgis_layer_details = self.get_qgis_layer_details()
        if qgis_layer_details is not None:
            layer = PluginGlobals.instance().iface.addVectorLayer(
                qgis_layer_details["uri"],
                qgis_layer_details["title"],
                qgis_layer_details["provider"],
            )
            if not layer or not layer.isValid():
                if layer:
                    QgsProject.instance().removeMapLayer(layer.id())
                InvalidLayer()


class WfsFeatureTypeFilterTreeNode(FavoritesTreeNode):
    """
    Tree node for a WFS feature type filter
    """

    def __init__(
        self,
        title,
        node_type=PluginGlobals.instance().NODE_TYPE_WFS_FEATURE_TYPE_FILTER,
        description=None,
        status=None,
        metadata_url=None,
        ident=None,
        params=None,
        bounding_boxes=None,
        parent_node=None,
    ):
        """ """
        FavoritesTreeNode.__init__(
            self,
            title,
            node_type,
            description,
            status,
            metadata_url,
            ident,
            params,
            bounding_boxes,
            parent_node,
        )

        self.filter = params.get("filter")
        self.can_be_added_to_map = True

        # Icon
        plugin_icons = PluginIcons.instance()
        self.icon = plugin_icons.wfs_layer_icon
        if self.status == PluginGlobals.instance().NODE_STATUS_WARN:
            self.icon = plugin_icons.warn_icon

    def get_qgis_layer_details(self):
        """
        Return the details of the layer used by QGIS to add the layer to the map.
        This dictionary is used by the run_add_to_map_action and layerMimeData methods.
        """

        if self.parent_node is None:
            return None

        first_param_prefix = "?"
        if "?" in self.parent_node.service_url:
            first_param_prefix = "&"

        uri = u"{}{}SERVICE=WFS&VERSION={}&REQUEST=GetFeature&TYPENAME={}&SRSNAME={}".format(
            self.parent_node.service_url,
            first_param_prefix,
            self.parent_node.wfs_version,
            self.parent_node.feature_type_name,
            self.parent_node.layer_srs,
        )

        if self.filter:
            uri += "&Filter={}".format(self.filter)

        qgis_layer_uri_details = {
            "type": "vector",
            "provider": "WFS",
            "title": self.title,
            "uri": uri,
        }

        return qgis_layer_uri_details

    def run_add_to_map_action(self):
        """
        Add the WFS feature type to the map with a filter
        """

        qgis_layer_details = self.get_qgis_layer_details()
        if qgis_layer_details is not None:
            layer = PluginGlobals.instance().iface.addVectorLayer(
                qgis_layer_details["uri"],
                qgis_layer_details["title"],
                qgis_layer_details["provider"],
            )
            if not layer or not layer.isValid():
                if layer:
                    QgsProject.instance().removeMapLayer(layer.id())
                InvalidLayer()


class GdalWmsConfigFileTreeNode(FavoritesTreeNode):
    """
    Tree node for a GDAL WMS config file
    """

    def __init__(
        self,
        title,
        node_type=PluginGlobals.instance().NODE_TYPE_GDAL_WMS_CONFIG_FILE,
        description=None,
        status=None,
        metadata_url=None,
        ident=None,
        params=None,
        bounding_boxes=None,
        parent_node=None,
    ):
        """ """
        FavoritesTreeNode.__init__(
            self,
            title,
            node_type,
            description,
            status,
            metadata_url,
            ident,
            params,
            bounding_boxes,
            parent_node,
        )

        self.gdal_config_file_path = os.path.join(
            PluginGlobals.instance().config_dir_path, params.get("file_path")
        )
        self.can_be_added_to_map = True

        # Icon
        plugin_icons = PluginIcons.instance()
        self.icon = plugin_icons.raster_layer_icon
        if self.status == PluginGlobals.instance().NODE_STATUS_WARN:
            self.icon = plugin_icons.warn_icon

    def get_qgis_layer_details(self):
        """
        Return the details of the layer used by QGIS to add the layer to the map.
        This dictionary is used by the run_add_to_map_action and layerMimeData methods.
        """
        qgis_layer_uri_details = {
            "type": "raster",
            "provider": "gdal",
            "title": self.title,
            "uri": self.gdal_config_file_path.replace("\\", "/"),
        }

        return qgis_layer_uri_details

    def run_add_to_map_action(self):
        """
        Add the preconfigured TMS layer to the map
        """
        # PluginGlobals.instance().iface.addRasterLayer(self.gdal_config_file_path, self.title)
        qgis_layer_details = self.get_qgis_layer_details()
        if qgis_layer_details is not None:
            layer = PluginGlobals.instance().iface.addRasterLayer(
                qgis_layer_details["uri"], qgis_layer_details["title"]
            )
            if not layer or not layer.isValid():
                if layer:
                    QgsProject.instance().removeMapLayer(layer.id())
                InvalidLayer()
