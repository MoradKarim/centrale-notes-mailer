from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import smtplib
from email.message import EmailMessage
import time
import tempfile
import os

app = Flask(__name__)

# ✅ Identifiants fixes
EMAIL_ADDRESS = "your email"
EMAIL_PASSWORD = "your passeword"

# 🏠 Route principale (affiche l’interface)
@app.route('/')
def home():
    return render_template('index.html')

# 📎 Route pour servir le logo (ex: logo.png dans le même dossier que app.py)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# 📤 Route pour envoyer les mails depuis Excel
@app.route('/send-mails', methods=['POST'])
def send_mails():
    try:
        fichier = request.files['fichier']

        # Lecture temporaire du fichier Excel
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            fichier.save(tmp.name)
            df = pd.read_excel(tmp.name)

        # Connexion SMTP à Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        log = []

        for index, row in df.iterrows():
            nom = row['Nom']
            email = row['Email']
            math = row['Math']
            physique = row['Physique']
            info = row['Info']

            message = f"""\
Bonjour {nom},

Voici vos notes personnelles :

- Math : {math}
- Physique : {physique}
- Informatique : {info}

Bonne continuation,
L'administration
"""

            msg = EmailMessage()
            msg['Subject'] = f"Notes de {nom} – Résultats scolaires"
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = email
            msg.set_content(message)

            try:
                server.send_message(msg)
                log.append(f"✅ Mail envoyé à {nom} ({email})")
                time.sleep(1)
            except Exception as e:
                log.append(f"❌ Erreur pour {email} : {str(e)}")

        server.quit()
        print("✅ Tous les mails ont été envoyés.")
        return jsonify({"message": "\n".join(log)})

    except Exception as e:
        print("❌ Erreur générale :", e)
        return jsonify({"message": f"Erreur générale : {str(e)}"}), 500

# 🚀 Lancement local
if __name__ == '__main__':
    app.run(debug=True)
