# -*- coding: utf-8 -*-

import os
import json

from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsNetworkAccessManager,
    QgsNetworkReplyContent,
)
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtCore import QUrl


from rgd.utils.plugin_globals import PluginGlobals
from .nodes import (
    WmsLayerTreeNode,
    WmsStyleLayerTreeNode,
    WmtsLayerTreeNode,
    WfsFeatureTypeTreeNode,
)
from .nodes import (
    WfsFeatureTypeFilterTreeNode,
    GdalWmsConfigFileTreeNode,
    FolderTreeNode,
)


def download_tree_config_file(file_url):
    """
    Download the resources tree file
    """
    try:
        # replace content of local config file by content of online config file
        with open(PluginGlobals.instance().config_file_path, "w") as local_config_file:

            request = QNetworkRequest(QUrl(file_url))
            manager = QgsNetworkAccessManager.instance()
            response: QgsNetworkReplyContent = manager.blockingGet(
                request, forceRefresh=True
            )

            if response.error() != QNetworkReply.NoError:
                raise Exception(f"{response.error()} - {response.errorString()}")

            data_raw_string = bytes(response.content()).decode("utf-8")
            data = json.loads(data_raw_string)

            json.dump(data, local_config_file, ensure_ascii=False, indent=2)

    except Exception as e:
        short_message = "Le téléchargement du fichier de configuration du plugin {0} a échoué.".format(
            PluginGlobals.instance().PLUGIN_TAG
        )
        PluginGlobals.instance().iface.messageBar().pushMessage(
            "Erreur", short_message, level=Qgis.Critical
        )

        long_message = "{0}\nUrl du fichier : {1}\n{2}\n{3}".format(
            short_message, file_url, e.__doc__, e
        )
        QgsMessageLog.logMessage(
            long_message, tag=PluginGlobals.instance().PLUGIN_TAG, level=Qgis.Critical
        )


class TreeNodeFactory:
    """
    Class used to build FavoritesTreeNode instances
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.root_node = None

        if not os.path.isfile(self.file_path):
            message = "Le fichier de configuration du plugin {0} n'a pas pu être trouvé.".format(
                PluginGlobals.instance().PLUGIN_TAG
            )
            PluginGlobals.instance().iface.messageBar().pushMessage(
                "Erreur", message, level=Qgis.Critical
            )
            QgsMessageLog.logMessage(
                message, tag=PluginGlobals.instance().PLUGIN_TAG, level=Qgis.Critical
            )
            return

        try:
            # Read the config file
            # QgsMessageLog.logMessage("Config file path: {}".format(self.file_path,
            #                                                        tag=PluginGlobals.instance().PLUGIN_TAG,
            #                                                        level=Qgis.Info))
            with open(self.file_path) as f:
                config_string = "".join(f.readlines())
                config_struct = json.loads(config_string)
                self.root_node = self.build_tree(config_struct)

        except Exception as e:
            short_message = "La lecture du fichier de configuration du plugin {0} a produit des erreurs.".format(
                PluginGlobals.instance().PLUGIN_TAG
            )
            PluginGlobals.instance().iface.messageBar().pushMessage(
                "Erreur", short_message, level=Qgis.Critical
            )

            long_message = "{0}\n{1}\n{2}".format(short_message, e.__doc__, e)
            QgsMessageLog.logMessage(
                long_message,
                tag=PluginGlobals.instance().PLUGIN_TAG,
                level=Qgis.Critical,
            )

    def build_tree(self, tree_config, parent_node=None):
        """
        Function that do the job
        """

        # Read the node attributes
        node_title = tree_config.get("title", None)
        node_description = tree_config.get("description", None)
        node_type = tree_config.get("type", None)
        node_status = tree_config.get("status", None)
        node_metadata_url = tree_config.get("metadata_url", None)
        node_ident = tree_config.get("ident", None)
        node_params = tree_config.get("params", None)
        node_bounding_boxes = tree_config.get("bounding_boxes", None)
        requires_auth = tree_config.get("requires_auth", False)

        if node_title:
            # Creation of the node
            if node_type == PluginGlobals.instance().NODE_TYPE_WMS_LAYER:
                node = WmsLayerTreeNode(
                    node_title,
                    node_type,
                    node_description,
                    node_status,
                    node_metadata_url,
                    node_ident,
                    node_params,
                    node_bounding_boxes,
                    requires_auth,
                    parent_node,
                )

            elif node_type == PluginGlobals.instance().NODE_TYPE_WMS_LAYER_STYLE:
                node = WmsStyleLayerTreeNode(
                    node_title,
                    node_type,
                    node_description,
                    node_status,
                    node_metadata_url,
                    node_ident,
                    node_params,
                    node_bounding_boxes,
                    requires_auth,
                    parent_node,
                )

            elif node_type == PluginGlobals.instance().NODE_TYPE_WMTS_LAYER:
                node = WmtsLayerTreeNode(
                    node_title,
                    node_type,
                    node_description,
                    node_status,
                    node_metadata_url,
                    node_ident,
                    node_params,
                    node_bounding_boxes,
                    requires_auth,
                    parent_node,
                )

            elif node_type == PluginGlobals.instance().NODE_TYPE_WFS_FEATURE_TYPE:
                node = WfsFeatureTypeTreeNode(
                    node_title,
                    node_type,
                    node_description,
                    node_status,
                    node_metadata_url,
                    node_ident,
                    node_params,
                    node_bounding_boxes,
                    requires_auth,
                    parent_node,
                )

            elif (
                node_type == PluginGlobals.instance().NODE_TYPE_WFS_FEATURE_TYPE_FILTER
            ):
                node = WfsFeatureTypeFilterTreeNode(
                    node_title,
                    node_type,
                    node_description,
                    node_status,
                    node_metadata_url,
                    node_ident,
                    node_params,
                    node_bounding_boxes,
                    parent_node,
                )

            elif node_type == PluginGlobals.instance().NODE_TYPE_GDAL_WMS_CONFIG_FILE:
                node = GdalWmsConfigFileTreeNode(
                    node_title,
                    node_type,
                    node_description,
                    node_status,
                    node_metadata_url,
                    node_ident,
                    node_params,
                    node_bounding_boxes,
                    parent_node,
                )

            else:
                node = FolderTreeNode(
                    node_title,
                    node_type,
                    node_description,
                    node_status,
                    node_metadata_url,
                    node_ident,
                    node_params,
                    node_bounding_boxes,
                    parent_node,
                )

            # Creation of the node children
            node_children = tree_config.get("children", [])
            if len(node_children) > 0:
                for child_config in node_children:
                    child_node = self.build_tree(child_config, node)
                    node.children.append(child_node)

            return node

        else:
            return None
