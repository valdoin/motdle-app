from flask import Flask, jsonify, send_from_directory, request
import random
from azure.storage.blob import BlobServiceClient
import os
from datetime import datetime,timedelta
import pyodbc

app = Flask(__name__, static_folder="static")

# Nom du conteneur et fichier Blob
CONTAINER_NAME = "motdlecontainer"
BLOB_NAME = "listemots.txt"
# Configuration de connexion bd
DB_SERVER = "tcp:motdle-serverv2.database.windows.net"
DB_NAME = "motdle-bd"
DB_USERNAME = os.getenv("DB_USERNAME") 
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_db_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={DB_SERVER},1433;"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USERNAME};"  
        f"PWD={DB_PASSWORD};"  
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

def record_past_word(word):
    """Enregistrer un mot dans la table past_words."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO past_words (word, date_used) VALUES (?, ?)", (word, datetime.now().date()))
            conn.commit()
    finally:
        conn.close()

def get_daily_word():
    """Récupère un mot aléatoire depuis Azure Blob Storage."""
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING n'est pas défini dans les variables d'environnement.")
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(BLOB_NAME)
    mots = blob_client.download_blob().content_as_text().splitlines()
    mot_du_jour = random.choice(mots)
    # Enregistrer le mot dans la base de données
    record_past_word(mot_du_jour)
    return mot_du_jour

def increment_users_found(word):
    """Incrémenter le compteur de users_found pour un mot donné."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE past_words SET users_found = users_found + 1 WHERE word = ? AND date_used = ?", (word, datetime.now().date()))
            conn.commit()
    finally:
        conn.close()


@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/mot", methods=["GET"])
def get_mot():
    """Endpoint pour récupérer le mot du jour et les stats du mot précédent."""
    try:
        date_aujourdhui = datetime.now().date()
        date_hier = (datetime.now() - timedelta(days=1)).date()

        # Récupérer le mot du jour et le nombre d'utilisateurs ayant trouvé le mot depuis la base de données
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT word, users_found FROM past_words WHERE date_used = ?", (date_aujourdhui,))
            row = cursor.fetchone()
            if row:
                mot = row[0]
                users_found_today = row[1]
            else:
                mot = get_daily_word()  # Générer un mot s'il n'existe pas encore pour aujourd'hui
                users_found_today = 0

            # Récupérer les stats du mot précédent
            cursor.execute("SELECT word, users_found FROM past_words WHERE date_used = ?", (date_hier,))
            row = cursor.fetchone()
            mot_precedent = {"word": row[0], "users_found": row[1]} if row else {"word": None, "users_found": 0}

        return jsonify({"mot": mot, "mot_precedent": mot_precedent, "users_found_today": users_found_today})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route("/api/stats", methods=["GET"])
def get_past_words_stats():
    """Récupère les statistiques des mots passés."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT word, date_used, users_found FROM past_words ORDER BY date_used DESC")
            rows = cursor.fetchall()
            stats = [{"word": row[0], "date": row[1].strftime("%Y-%m-%d"), "users_found": row[2]} for row in rows]
        return jsonify({"stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/found", methods=["POST"])
def mark_word_as_found():
    """Marquer un mot comme trouvé."""
    try:
        data = request.json
        word = data.get("word")
        if not word:
            return jsonify({"error": "Le mot est requis"}), 400
        increment_users_found(word)
        return jsonify({"message": "Mot trouvé mis à jour avec succès"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)