from flask import Flask, render_template, request, redirect, session, url_for
import requests

app = Flask(__name__)

api_service_url = 'http://api_back:5000'
auth_url = 'http://api_auth:5020'
url = api_service_url + "/"
with open("public_key.pem", "r") as key_file:
    app.secret_key = key_file.read()

@app.before_request
def check_login():
    # Rediriger automatiquement les utilisateurs non connectés vers /login sauf pour certaines routes
    chemins_exclus = ['login', 'static']  # Exclure login et les fichiers statiques
    if 'token' not in session and request.endpoint not in chemins_exclus:
        return redirect(url_for('login'))
    
@app.route('/')
def index():
    return render_template('index.j2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    err_id = False
    if request.method == 'POST':
        id = request.form.get('id')
        mdp = request.form.get('mdp')
        try:
            # Envoi des identifiants à l'API FastAPI
            response = requests.post(f"{auth_url}/login", data={'id': id, 'mdp': mdp})
            
            if response.status_code == 200:
                response_json = response.json()
                if "access_token" in response_json:
                    token = response_json.get("access_token")  # Récupérer le token
                    if token:
                        session['token'] = token  # Stocker le token dans la session
                        return redirect(url_for('index'))  # Rediriger vers l'index

            # Si les identifiants sont invalides
            err_id = True
            # Ne pas rediriger ici, mais plutôt passer `err_id` au template
        except requests.RequestException as e:
            # Gestion des erreurs de connexion au serveur d'authentification
            err_id = True
            return f"Erreur de connexion au serveur d'authentification : {str(e)}", 500

    # Afficher le formulaire de connexion avec err_id passé au template
    return render_template('login.j2', err_id=err_id)

@app.route('/protected')
def protected():
    # Vérifier si l'utilisateur est connecté
    if 'token' not in session:
        return redirect(url_for('login'))
    return f"Connexion réussie, token: {session['token']}"

@app.route('/logout')
def logout():
    session.pop('token', None)  # Supprime le token de la session
    return redirect(url_for('login'))  # Redirige vers la page de connexion

@app.route('/utilisateurs')
def utilisateurs():
    url_utilisateurs = url+'/utilisateurs'
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = requests.get(url_utilisateurs,headers=headers)
    lst_users = resp.json()
    nom_colonne=[
                 "ID",
                 "Nom",
                 "Email",
                 "Nombre de livre(s) emprunté"
                ]
    return render_template('utilisateurs.j2', lst=lst_users, col=nom_colonne)

@app.route('/livres')
def livres():
    url_livres = url+'/livres'
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = requests.get(url_livres,headers=headers)
    lst_livres = resp.json()
    nom_colonne=[
                 "ID",
                 "Titre",
                 "Résumé",
                 "Date",
                 "Nom de l'auteur",
                 "Disponibilité"
                ]
    return render_template('livres.j2', lst=lst_livres, col=nom_colonne)

@app.route('/auteurs')
def auteurs():
    url_auteurs = url+'/auteurs'
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}    
    resp = requests.get(url_auteurs,headers=headers)
    lst_auteur = resp.json()
    nom_colonne=[
                 "ID",
                 "Nom"
                ]
    return render_template('auteurs.j2', lst=lst_auteur, col=nom_colonne)

@app.route('/utilisateur/', methods=['POST'])
def find_users():
    utilisateur = request.form.get("recherche_users")
    url_recherche_utilisateurs = f"{url}/utilisateur/{utilisateur}"
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}    
    resp = requests.get(url_recherche_utilisateurs, headers=headers)
    if resp.status_code == 200:
        nom_colonne = ["ID", "Nom", "Email", "Nombre de livre(s) emprunté"]
        return render_template('recherche_utilisateur.j2', lst=resp.json(), col=nom_colonne)
    else:
        url_utilisateurs = url+'/utilisateurs'
        url_recherche_utilisateurs = f"{url}/utilisateur/{utilisateur}"
        token = session.get("token")        
        resp = requests.get(url_utilisateurs,headers=headers)
        lst_users = resp.json()
        nom_colonne=[
                    "ID",
                    "Nom",
                    "Email",
                    "Nombre de livre(s) emprunté"
                    ]
        return render_template('utilisateurs.j2', lst=lst_users, col=nom_colonne)
    
@app.route('/livres/siecle/', methods=['POST'])
def find_siecle():
    numero = request.form.get("recherche_siecle")
    url_recherche_siecle = f"{url}/livres/siecle/{numero}"
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}    
    resp = requests.get(url_recherche_siecle, headers=headers)
    nom_colonne=[
                 "ID",
                 "Titre",
                 "Résumé",
                 "Date",
                 "Nom de l'auteur",
                 "Disponibilité"
                ]
    return render_template('recherche_siecle.j2', lst=resp.json(), col=nom_colonne)
    
if __name__ == '__main__':
    app.run(port=5010, host="0.0.0.0")