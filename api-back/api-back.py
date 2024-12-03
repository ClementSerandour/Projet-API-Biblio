#FASTAPI
from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from starlette.responses import RedirectResponse
import sqlite3
 
# Initialisation de l'application
app = FastAPI()
database = "data/database.db"

@app.middleware("http")
async def middleware_authentification(request: Request, call_next):
    chemins_exclus = ["/openapi.json", "/docs"]  # Chemins qui n'exigent pas d'authentification
    chemin = request.url.path
    
    # Si le chemin est exclu, poursuivre sans vérifier le token
    if chemin in chemins_exclus:
        return await call_next(request)

    # Récupérer le token d'authentification dans les headers
    authorization: str = request.headers.get("Authorization")
    
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(content="Non autorisé, vous n'avez pas de token")  # Redirection en cas d'absence ou d'invalidité du token

    # Extraire le token après "Bearer "
    token = authorization[len("Bearer "):]
    
    # Logique de validation du token (exemple : vérifier si le token est "example_token")
    if token != token:
        raise HTTPException(status_code=401, detail="Token invalide")

    return await call_next(request)

@app.get('/')
async def index():
    return JSONResponse(content={'message':'Hello World'})

@app.get("/utilisateurs")
async def get_utilisateurs():
    """
    Liste tous les utilisateurs.
    """
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM utilisateurs")
        lst_users = cur.fetchall()
        result = []
        for i in lst_users:
            result.append({"id":i[0],"nom":i[1],"email":i[3],"livres_emprunter":i[4]})
    return JSONResponse(content=result)

@app.get("/livres")
async def get_livres():
    """
    Liste tous les livres.
    """
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Livres")
        lst_livres = cur.fetchall()
        result = []
        for i in lst_livres:
            auteur_id=i[4]
            users_id=i[5]
            cur.execute("SELECT nom_auteur FROM Auteurs WHERE id=?",(auteur_id,))
            nom_auteur=cur.fetchone()[0] or 0
            cur.execute("SELECT nom FROM utilisateurs WHERE id=?",(users_id,))
            nom_users=cur.fetchone()
            if nom_users is not None:
                nom_users='Indisponible'
            else: nom_users='Disponible'
            result.append({"id":i[0],"titre":i[1],"pitch":i[2],"date_public":i[3],"nom_auteur":nom_auteur,"disponibilite":nom_users})
    return JSONResponse(content=result)

@app.get("/auteurs")
async def get_auteurs():
    """
    Liste tous les auteurs.
    """
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Auteurs")
        lst_auteurs = cur.fetchall()
        result = []
        for i in lst_auteurs:
            result.append({"id":i[0],"nom_auteurs":i[1]})
    return JSONResponse(content=result)

@app.get("/utilisateur/{utilisateur}")
async def find_user(utilisateur: str):
    """
    Recherche d'utilisateur par ID ou nom.
    """
    if utilisateur.isdigit() == True:
        with sqlite3.connect(database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM utilisateurs WHERE id=?", (utilisateur,))
            users = cur.fetchall()
            result = []
            for i in users:
                result.append({"id":i[0],"nom":i[1],"email":i[3],"livres_emprunter":i[4]})
        return JSONResponse(content=result)
    else:
        with sqlite3.connect(database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM utilisateurs WHERE nom=?", (utilisateur,))
            users = cur.fetchall()
            if len(users) > 1:
                return JSONResponse(content="Il y a plus d'un utilisateur", status_code=400)
            elif len(users) == 0:
                return JSONResponse(content="Utilisateur inconnu", status_code=400)
            result = []
            for i in users:
                result.append({"id":i[0],"nom":i[1],"email":i[3],"livres_emprunter":i[4]})
        return JSONResponse(content=result)

@app.get("/utilisateur/emprunts/{utilisateur}")
async def livres_emprunter(utilisateur: str):
    """
    Liste les livres empruntés par un utilisateur.
    """
    if utilisateur.isdigit() == True:
        with sqlite3.connect(database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Livres WHERE emprunteur_id=?", (utilisateur,))
            lst_livres = cur.fetchall()
            result = []
            for i in lst_livres:
                result.append({"id":i[0],"titre":i[1],"pitch":i[2],"date_public":i[3],"auteur_id":i[4],"emprunteur_id":i[5]})
        return JSONResponse(content=result)
    else:
        with sqlite3.connect(database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM utilisateurs WHERE nom=?", (utilisateur,))
            id_emprunteur = cur.fetchall()
            if len(id_emprunteur) == 0:
                return JSONResponse(content="Il n'y a pas d'utilisateurs avec ce nom !")
            elif len(id_emprunteur) > 1:
                return JSONResponse(content="Il y a plus d'un utilisateurs portant ce nom !")
            else:
                id_emprunteur=id_emprunteur[0]
                id_emprunteur=id_emprunteur[0]
                cur = conn.cursor()
                cur.execute("SELECT * FROM Livres WHERE emprunteur_id=?", (id_emprunteur,))
                lst_livres = cur.fetchall()
                result = []
                for i in lst_livres:
                    result.append({"id":i[0],"titre":i[1],"pitch":i[2],"date_public":i[3],"auteur_id":i[4],"emprunteur_id":i[5]})
            conn.commit()
            return JSONResponse(content=result)

@app.get("/livres/siecle/{numero}")#a revoir
async def livres_siecle(numero: str):
        with sqlite3.connect(database) as conn:
            cur = conn.cursor()
            start_siecle = int(numero+"00")
            end_siecle = start_siecle-99
            cur.execute("SELECT date_public, id FROM Livres")
            info_livres = cur.fetchall()
            result = []
            for i in info_livres:
                date = i[0]
                id=i[1]
                annee = str(date)[-4:]
                annee = int(annee)
                if annee >= end_siecle and annee <= start_siecle:
                    cur.execute("SELECT * FROM Livres WHERE id=?",(id,))
                    lst_livres = cur.fetchall()
                    for i in lst_livres:
                        auteur_id=i[4]
                        users_id=i[5]
                        cur.execute("SELECT nom_auteur FROM Auteurs WHERE id=?",(auteur_id,))
                        nom_auteur=cur.fetchone()[0] or 0
                        cur.execute("SELECT nom FROM utilisateurs WHERE id=?",(users_id,))
                        nom_users=cur.fetchone()
                        if nom_users is not None:
                            nom_users='Indisponible'
                        else: nom_users='Disponible'
                        result.append({"id":i[0],"titre":i[1],"pitch":i[2],"date_public":i[3],"nom_auteur":nom_auteur,"disponibilite":nom_users})
            return JSONResponse(content=result)

@app.post("/livres/ajouter")
async def livres_ajouter(titre: str, pitch: str, date: str, nom_auteur: str):
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        
        # Récupération du dernier ID des livres
        cur.execute("SELECT MAX(id) FROM Livres")
        last_id = cur.fetchone()[0] or 0
        id_livres = last_id + 1

        # Vérification de l'existence de l'auteur
        cur.execute("SELECT id FROM Auteurs WHERE nom_auteur = ?", (nom_auteur,))
        auteur = cur.fetchone()

        if auteur is None:  # Si l'auteur n'existe pas, l'ajouter
            cur.execute("SELECT MAX(id) FROM Auteurs")
            last_auteur_id = cur.fetchone()[0] or 0
            id_auteur = last_auteur_id + 1

            cur.execute(
                "INSERT INTO Auteurs (id, nom_auteur) VALUES (?, ?)",
                (id_auteur, nom_auteur),
            )
            conn.commit()
        else:
            id_auteur = auteur[0]

        # Ajout du livre dans la table Livres
        cur.execute(
            """
            INSERT INTO Livres (id, titre, pitch, date_public, auteur_id, emprunteur_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (id_livres, titre, pitch, date, id_auteur, 0),
        )
        conn.commit()

    return JSONResponse(content="Livre ajouté")

@app.post("/utilisateur/ajouter")
async def users_ajouter(nom: str, email:str, mdp:str):
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        # Récupération du dernier ID des livres
        cur.execute("SELECT MAX(id) FROM utilisateurs")
        last_id = cur.fetchone()[0] or 0
        id_users = last_id + 1

        cur.execute("INSERT INTO utilisateurs (id,nom,mot_de_passe,email) VALUES (?,?,?,?)",(id_users,nom,mdp,email,))
        result=[]
        result.append({"id":id_users,"nom":nom,"mot de passe":mdp,"email":email})
        conn.commit()
        return JSONResponse(content=result)

@app.delete("/utilisateur/<utilisateur>/supprimer")
async def users_ajouter(utilisateur:str):
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        # Récupération de l'id de l'utilisateur
        cur.execute("SELECT id FROM utilisateurs WHERE nom=?",(utilisateur,))
        id_users = cur.fetchall()
        #Vérification qu'il y ai qu'un seul utilisateur de ce nom
        if len(id_users) == 0:
            return JSONResponse(content={"message":"L'utilisateur n'existe pas"})
        elif len(id_users) > 1:
            return JSONResponse(content={"message":"Plusieurs utilisateurs ont le même nom"})

        id_users=id_users[0][0]
        cur.execute("DELETE FROM utilisateurs WHERE id=?",(id_users,))
        conn.commit()
        return JSONResponse(content={"message":"L'utilisateur "+utilisateur+" à été supprimé"})

@app.put("/utilisateur/{utilisateur_id}/emprunter/{livre_id}")
async def emprunt_livres(utilisateur_id:int,livre_id:int):
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT livre_emprunter FROM utilisateurs WHERE id=?",(utilisateur_id,))
        nbr_emprunt = cur.fetchone()[0] or 0
        if nbr_emprunt >= 4 :
            return JSONResponse(content={'message':"Nombre de livres max déjà emprunter"})
        cur.execute("SELECT emprunteur_id FROM Livres WHERE id=?",(livre_id,))
        livre_dispo = cur.fetchone()[0] or 0
        if livre_dispo != 0:
            return JSONResponse(content={'message':"Livre déjà emprunté"})
        cur.execute("UPDATE Livres SET emprunteur_id=? WHERE id=?",(utilisateur_id,livre_id,))
        conn.commit()
        return JSONResponse(content={'message':"Livres emprunté"})

@app.put("/utilisateur/{utilisateur_id}/rendre/{livre_id}")
async def retour_livres(utilisateur_id:int,livre_id:int):
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT emprunteur_id FROM Livres WHERE id=?",(livre_id,))
        verif_emprunt = cur.fetchone()[0] or 0
        if verif_emprunt != utilisateur_id:
            return JSONResponse(content={'message':"Ce livres n'est pas emprunter par l'utilisateur"})
        cur.execute("UPDATE Livres SET emprunteur_id=0 WHERE id=?",(livre_id,))
        conn.commit()
        return JSONResponse(content={'message':'Le livre à été rendu'})

import uvicorn
if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    uvicorn.run(app, host='0.0.0.0', port=5000)