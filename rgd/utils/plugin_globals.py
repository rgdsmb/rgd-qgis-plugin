# -*- coding: utf-8 -*-

import copy
import json
import os
from rgd.utils.singleton import Singleton
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.core import QgsApplication, QgsAuthMethodConfig

@Singleton
class PluginGlobals:
    """ """

    iface = None
    plugin_path = None

    # Plugin infos
    PLUGIN_NAME = u"RGD Savoie Mont-Blanc"
    PLUGIN_TAG = u"RGD"
    PLUGIN_VERSION = u"0.1"
    PLUGIN_SOURCE_REPOSITORY = u"https://github.com/rgdsmb/rgd-qgis-plugin"

    # Tree nodes types
    NODE_TYPE_FOLDER = "folder"
    NODE_TYPE_WS = "web_service"
    NODE_TYPE_WMS_LAYER = "wms_layer"
    NODE_TYPE_WMTS_LAYER = "wmts_layer"
    NODE_TYPE_WMS_LAYER_STYLE = "wms_layer_style"
    NODE_TYPE_WFS_FEATURE_TYPE = "wfs_feature_type"
    NODE_TYPE_WFS_FEATURE_TYPE_FILTER = "wfs_feature_type_filter"
    NODE_TYPE_GDAL_WMS_CONFIG_FILE = "gdal_wms_config_file"
    NODE_TYPE_XYZVECTORTILES_LAYER = "xyzvectortiles_layer"

    # Node status values
    NODE_STATUS_WARN = "warn"

    # Images dir
    IMAGES_DIR_NAME = "images"
    LOGO_FILE_NAME = "rgd.png"

    ICON_WARN_FILE_NAME = "Icon_Simple_Warn.png"
    ICON_WMS_LAYER_FILE_NAME = "mIconWms.svg"
    ICON_WMS_STYLE_FILE_NAME = "mIconWmsStyle.svg"
    ICON_WFS_LAYER_FILE_NAME = "mIconWfs.svg"
    ICON_RASTER_LAYER_FILE_NAME = "mIconRaster.svg"

    # Config files dir
    CONFIG_FILES_DOWNLOAD_AT_STARTUP = True
    CONFIG_DIR_NAME = "config"
    CONFIG_FILE_NAMES = ["config.json"]
    CONFIG_FILE_URLS_FACTORY = [
        "https://geoportail.rgd.fr/qgisconfig/config.json"
    ]
    CONFIG_FILE_URLS = copy.deepcopy(CONFIG_FILE_URLS_FACTORY)

    # Must be 7 characters
    FACTORY_AUTH_CONFIG_ID = "RGDOAU2"

    # Hide resources with status = warn
    HIDE_RESOURCES_WITH_WARN_STATUS = True

    # Hide empty group in the resources tree
    HIDE_EMPTY_GROUPS = True

    # Authentication configuration identifier
    AUTH_CONFIG_ID = None

    LOCALISATION_CADASTRALE_URL = "https://majicad.rgd74.fr/qgis/index.phtml"

    def __init__(self):
        """ """

        self.default_qsettings = {
            "CONFIG_FILES_DOWNLOAD_AT_STARTUP": self.CONFIG_FILES_DOWNLOAD_AT_STARTUP,
            "CONFIG_FILE_NAMES": self.CONFIG_FILE_NAMES,
            "CONFIG_FILE_URLS": self.CONFIG_FILE_URLS,
            "HIDE_RESOURCES_WITH_WARN_STATUS": self.HIDE_RESOURCES_WITH_WARN_STATUS,
            "HIDE_EMPTY_GROUPS": self.HIDE_EMPTY_GROUPS,
            "AUTH_CONFIG_ID": self.AUTH_CONFIG_ID,
        }

        self.config_dir_path = None
        self.config_file_path = None
        self.images_dir_path = None
        self.logo_file_path = None

    def set_plugin_path(self, plugin_path):
        """ """

        # system_encoding = sys.getfilesystemencoding()
        # self.plugin_path = plugin_path.decode(system_encoding)

        self.plugin_path = plugin_path

    def set_plugin_iface(self, iface):
        """ """

        self.iface = iface

    def reload_globals_from_qgis_settings(self):
        """
        Reloads the global variables of the plugin
        """

        # Read the qgis plugin settings
        s = QSettings()
        # False by default and u"0" so that parameter is checked the 1st time user opens plugin, else invert
        self.CONFIG_FILES_DOWNLOAD_AT_STARTUP = (
            False
            if s.value(
                u"{0}/config_files_download_at_startup".format(self.PLUGIN_TAG),
                self.CONFIG_FILES_DOWNLOAD_AT_STARTUP,
            )
            == u"0"
            else True
        )

        self.CONFIG_DIR_NAME = s.value(
            u"{0}/config_dir_name".format(self.PLUGIN_TAG), self.CONFIG_DIR_NAME
        )

        self.CONFIG_FILE_NAMES = s.value(
            u"{0}/config_file_names".format(self.PLUGIN_TAG), self.CONFIG_FILE_NAMES
        )

        self.CONFIG_FILE_URLS = s.value(
            u"{0}/config_file_urls".format(self.PLUGIN_TAG), self.CONFIG_FILE_URLS if self.CONFIG_FILE_URLS else ""
        )

        self.AUTH_CONFIG_ID = s.value(
            u"{0}/auth_config_id".format(self.PLUGIN_TAG), self.AUTH_CONFIG_ID
        )

        # False by default so that parameter is checked the 1st time user opens plugin, else invert
        self.HIDE_RESOURCES_WITH_WARN_STATUS = (
            False
            if s.value(
                u"{0}/hide_resources_with_warn_status".format(self.PLUGIN_TAG),
                self.HIDE_RESOURCES_WITH_WARN_STATUS,
            )
            == u"0"
            else True
        )

        # False by default so that parameter is checked the 1st time user opens plugin, else invert
        self.HIDE_EMPTY_GROUPS = (
            False
            if s.value(
                u"{0}/hide_empty_groups".format(self.PLUGIN_TAG), self.HIDE_EMPTY_GROUPS
            )
            == u"0"
            else True
        )

        self.config_dir_path = os.path.join(self.plugin_path, self.CONFIG_DIR_NAME)
        self.config_file_path = os.path.join(
            self.config_dir_path, self.CONFIG_FILE_NAMES[0]
        )

        self.images_dir_path = os.path.join(self.plugin_path, self.IMAGES_DIR_NAME)
        self.logo_file_path = os.path.join(self.images_dir_path, self.LOGO_FILE_NAME)

    def reset_to_defaults(self):
        """
        Reset global variables to default values
        """

        s = QSettings()
        s.setValue(u"{0}/hide_resources_with_warn_status".format(self.PLUGIN_TAG), u"1")
        s.setValue(u"{0}/hide_empty_groups".format(self.PLUGIN_TAG), u"1")
        s.setValue(
            u"{0}/config_files_download_at_startup".format(self.PLUGIN_TAG), u"1"
        )  # 0
        s.setValue(u"{0}/config_file_names".format(self.PLUGIN_TAG), ["config.json"])
        s.setValue(
            u"{0}/config_file_urls".format(self.PLUGIN_TAG),
            self.CONFIG_FILE_URLS_FACTORY,
        )
        s.setValue(u"{0}/auth_config_id".format(self.PLUGIN_TAG), self.FACTORY_AUTH_CONFIG_ID)

        s.setValue(u"{0}/show_dock".format(self.PLUGIN_TAG), u"1")

        auth_mgr = QgsApplication.authManager()
        auth_mgr.removeAuthenticationConfig(self.FACTORY_AUTH_CONFIG_ID)
        self.create_oauth2_config()

    def get_qgis_setting_default_value(self, setting):
        """ """

        return self.default_qsettings.get(setting, None)

    def set_qgis_settings_value(self, setting, value):
        """
        Update a settings value
        """

        s = QSettings()

        # Convert boolean in unicode string
        if type(value) == bool:
            value = u"1" if value else u"0"

        # Save the settings value
        s.setValue(u"{0}/{1}".format(self.PLUGIN_TAG, setting), value)

        # Reload all settings values
        self.reload_globals_from_qgis_settings()


    def create_oauth2_config(self):

        auth_mgr = QgsApplication.authManager()

        if self.FACTORY_AUTH_CONFIG_ID not in auth_mgr.availableAuthMethodConfigs():

            if not auth_mgr.masterPasswordIsSet():
                QMessageBox(QMessageBox.Icon.Information,
                            "Initialisation de l'extension RGD Savoie Mont-Blanc",
                            "L'extension RGD Savoie Mont-Blanc va initialiser sa configuration pour l'authentification OAuth2 (SSO). Il va vous être demandé de saisir le mot de passe principal protégeant la base de données QGIS de configurations d'authentification (Wallet/Keyring)").exec()

            config = {
                "accessMethod":0,
                "apiKey":"",
                "clientId":"SIGDesktop-qeAPxX3K6qLJ35",
                "clientSecret":"",
                "configType":1,
                "grantFlow":3,
                "persistToken":False,
                "redirectHost":"127.0.0.1",
                "redirectPort":"7070",
                "redirectUrl":"qgis-client",
                "refreshTokenUrl":"https://login.rgd.fr/realms/rgd/protocol/openid-connect/token",
                "requestTimeout":"30",
                "requestUrl":"https://login.rgd.fr/realms/rgd/protocol/openid-connect/auth",
                "scope":"openid profile groups email",
                "tokenUrl":"https://login.rgd.fr/realms/rgd/protocol/openid-connect/token",
                "version":1
            }

            auth_cfg = QgsAuthMethodConfig("OAuth2")
            auth_cfg.setId(self.FACTORY_AUTH_CONFIG_ID)
            auth_cfg.setName("Configuration OAuth2 pour données de RGDSMB")
            auth_cfg.setConfig('oauth2config', json.dumps(config))

            if auth_mgr.storeAuthenticationConfig(auth_cfg):
                self.set_qgis_settings_value("auth_config_id", self.FACTORY_AUTH_CONFIG_ID)
            if self.FACTORY_AUTH_CONFIG_ID not in auth_mgr.availableAuthMethodConfigs():
                QMessageBox(QMessageBox.Icon.Warning,
                        "Initialisation de l'extension RGD Savoie Mont-Blanc",
                        "Erreur lors de la tentative d'enregistrement de la configuration pour l'authentification OAuth2 (SSO)").exec()
