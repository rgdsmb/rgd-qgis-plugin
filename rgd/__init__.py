# -*- coding: utf-8 -*-


def classFactory(iface):
    from .plugin import SimpleAccessPlugin

    return SimpleAccessPlugin(iface)
