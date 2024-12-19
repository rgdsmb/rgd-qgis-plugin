import json

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtNetwork import QNetworkReply


def get_json_response(reply):
    if reply.error() == QNetworkReply.NetworkError.OperationCanceledError:
        return None
    response = reply.readAll()
    if reply.error() != QNetworkReply.NetworkError.NoError:
        box = QMessageBox(QMessageBox.Icon.Warning, "Erreur lors de la requête",
                          "L'erreur '" + reply.errorString() + "' s'est produite: " + bytes(response).decode('utf-8'))
        box.exec()
        return None
    try:
        response = json.loads(bytes(response))
        return response
    except Exception:
        box = QMessageBox(QMessageBox.Icon.Warning, "Erreur lors de la requête",
                          "La réponse du serveur n'est pas au format JSON: " + bytes(response).decode('utf-8'))
        box.exec()
        return None
