'''
Si desidera realizzare una semplice applicazione web,
si prenda come riferimento la ToDo App presente in piattaforma,
che dovrà fornire una bacheca messaggi condivisa, visibile a tutti gli utenti registrati.

L’obiettivo dell’applicazione è permettere agli utenti di:
- Registrarsi creando un nuovo account con email e password.
- Accedere tramite login.
- Pubblicare un messaggio testuale sulla bacheca.
- Visualizzare tutti i messaggi pubblicati da qualunque utente, non soltanto i propri.

Ogni messaggio dovrà contenere:
il testo del messaggio;
l’autore, identificato dall’email dell’utente;
la data e ora di pubblicazione.

Tutti gli utenti autenticati devono poter visualizzare l’intera bacheca, compresi i messaggi inseriti dagli altri utenti.
'''

#   importa il client asincrono di mongodb dalla lib pymongo
from pymongo import AsyncMongoClient

#   parametri statici, url del container db e nome del db che si vuole creare
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "task_app"

#   chiave di cifratura hash e port number della web app
COOKIE_KEY = "hybrid_theory_linkin_park"
PORT_NUMBER_APP = 8888

#   crea il client collegato al container e crea il database
client = AsyncMongoClient(MONGO_URL)
db = client[DB_NAME]

#   crea la collezione degli utenti e delle task
users = db["users"]
tasks = db["tasks"]