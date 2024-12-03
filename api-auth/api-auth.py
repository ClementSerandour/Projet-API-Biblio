#FASTAPI
from fastapi import FastAPI, Depends, HTTPException,Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sqlite3,jwt

# Initialisation de l'application
app = FastAPI()
database = "data/database.db"

security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        with open('public_key.pem', 'r') as file:
            public_key = file.read()
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

@app.post("/login")
async def login(id: str = Form(...), mdp: str = Form(...)):
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT nom,mot_de_passe FROM utilisateurs")
        lst_users = cur.fetchall()
        for username, password in lst_users:
            if username == id and password == mdp:
                with open('private_key.pem', 'r') as file:
                    private_key = file.read()
                token = jwt.encode({'id': id}, private_key, algorithm="RS256")
                return {"access_token": token}
    return {"error": "Identifiants incorrects"}, 401

import uvicorn
if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    uvicorn.run(app, host='0.0.0.0', port=5020)
