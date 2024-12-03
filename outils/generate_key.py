from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_keys(nom_priv_key: str, nom_public_key: str):
    # Générer la clé privée
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Exporter la clé privée avec le nom spécifié
    with open(nom_priv_key, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Générer et exporter la clé publique avec le nom spécifié
    public_key = private_key.public_key()
    with open(nom_public_key, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    return private_key, public_key

# Exemple d'utilisation
generate_keys("private_key.pem", "public_key.pem")
