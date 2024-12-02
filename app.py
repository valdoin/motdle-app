from flask import Flask, jsonify, send_from_directory
import random
from azure.storage.blob import BlobServiceClient
import os
from datetime import datetime

app = Flask(__name__, static_folder="static")

# Nom du conteneur et fichier Blob
CONTAINER_NAME = "motdlecontainer"
BLOB_NAME = "listemots.txt"

# Cache pour stocker le mot du jour
mot_du_jour_cache = {"date": None, "mot": None}

def get_daily_word():
    """Récupère un mot aléatoire depuis Azure Blob Storage."""
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING n'est pas défini dans les variables d'environnement.")
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(BLOB_NAME)
    
    # Lire le fichier de mots depuis le blob
    mots = blob_client.download_blob().content_as_text().splitlines()
    return random.choice(mots)


@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/mot", methods=["GET"])
def get_mot():
    """Endpoint pour récupérer le mot du jour."""
    try:
        # Générer la clé du jour basée sur la date actuelle
        date_aujourdhui = datetime.now().strftime("%Y-%m-%d")
        
        # Vérifier si le mot du jour est déjà dans le cache pour cette date
        if mot_du_jour_cache["date"] == date_aujourdhui:
            mot = mot_du_jour_cache["mot"]
        else:
            # Nouveau jour : récupérer un nouveau mot et mettre à jour le cache
            mot = get_daily_word()
            mot_du_jour_cache["date"] = date_aujourdhui
            mot_du_jour_cache["mot"] = mot
        
        return jsonify({"mot": mot})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)