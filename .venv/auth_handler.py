import tornado.web
import tornado.escape
import bcrypt
from backend.db import users

#   handler iniziale
class BaseHandler(tornado.web.RequestHandler):

    #   richiede il cookie dell'utente
    def get_current_user(self):

        #   estrae il secure cookie dall'utente
        user_cookie = self.get_secure_cookie("user")

        #   se il cookie non esiste / compromesso ritorna None
        if not user_cookie:
            return None

        #   ritorna l'oggetto cookie decodificato da json
        return tornado.escape.json_decode(user_cookie)

    #   risposta json al client
    def write_json(self, data, status=200):

        #   status code 200 = OK
        self.set_status(status)

        #   imposta l'header risposta come json
        self.set_header("Content-Type", "application/json")

        #   ritorna il parametro dati on json al client
        self.write(tornado.escape.json_encode(data))

#   handler della registrazione dell'utente
class RegisterHandler(BaseHandler):

    #   richiesta POST
    async def post(self):

        #   estrazione dei dati passati dal body della richiesta e conversione da json a oggetti python
        body = tornado.escape.json_decode(self.request.body)

        #   estrazione dell'email e password dal body della richiesta
        email = body.get("email", "").strip()
        password = body.get("password", "")

        #   se non è stata data una password o una email richiama la funzione write_json con messaggio di errore e status code 400
        if not email or not password:
            return self.write_json({"error": "Email e password obbligatorie"}, 400)

        #   controlla se ci si sta cercando di registrare con la stessa email di un utente già esistente
        existing = await users.find_one({"email": email})
        if existing:

            #   richiama write_json con status code 400 e messaggio di errore
            return self.write_json({"error": "Utente già registrato"}, 400)

        #   criptazione della password del nuovo utente
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        #   inserimento nella collezione del db degli utenti email e password criptata
        await users.insert_one({
            "email": email,
            "password": hashed
        })

        #   richiama self_write con status code 201 e messaggio di conferma registrazione
        return self.write_json({"message": "Registrazione completata"}, 201)

#   handler delle richieste di LOGIN
class LoginHandler(BaseHandler):

    #   richiesta POST
    async def post(self):

        #   estrae dal body della richiesta gli oggetti python convertendoli dal formato iniziale json
        body = tornado.escape.json_decode(self.request.body)

        #   estrae dal body email e password
        email = body.get("email", "").strip()
        password = body.get("password", "")

        #   se non esistono utenti con la mail indicata ritorna errore al client
        user = await users.find_one({"email": email})
        if not user:
            return self.write_json({"error": "Credenziali errate"}, 401)

        #   controlla che anche la password (criptata) sia corretta, se non lo è ritorna messaggio di errore
        if not bcrypt.checkpw(password.encode(), user["password"]):
            return self.write_json({"error": "Credenziali errate"}, 401)

        #   creazione dizionario con dati dell'utente
        user_data = {
            "id": str(user["_id"]),
            "email": user["email"]
        }

        #   creazione cookie sicuro dell'utente
        self.set_secure_cookie("user", tornado.escape.json_encode(user_data))

        #   ritorna messaggio di successo al client ed i suoi dati
        return self.write_json({"message": "Login effettuato", "user": user_data})

#   handler della richiesta di LOGOUT
class LogoutHandler(BaseHandler):

    #   richiesta POST
    async def post(self):

        #   rimuove il cookie all'utente
        self.clear_cookie("user")

        #   messaggio di conferma del logout
        return self.write_json({"message": "Logout effettuato"})