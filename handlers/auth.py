import tornado.web
import tornado.escape
import bcrypt
from backend.db import users


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_cookie = self.get_secure_cookie("user")
        if not user_cookie:
            return None
        return tornado.escape.json_decode(user_cookie)

    def write_json(self, data, status=200):
        self.set_status(status)
        self.set_header("Content-Type", "application/json")
        self.write(tornado.escape.json_encode(data))


class RegisterHandler(BaseHandler):
    async def post(self):
        body = tornado.escape.json_decode(self.request.body)
        email = body.get("email", "").strip()
        password = body.get("password", "")

        if not email or not password:
            return self.write_json({"error": "Email e password obbligatorie"}, 400)

        existing = await users.find_one({"email": email})
        if existing:
            return self.write_json({"error": "Utente già registrato"}, 400)

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        await users.insert_one({
            "email": email,
            "password": hashed
        })

        return self.write_json({"message": "Registrazione completata"}, 201)


class LoginHandler(BaseHandler):
    async def post(self):
        body = tornado.escape.json_decode(self.request.body)
        email = body.get("email", "").strip()
        password = body.get("password", "")

        user = await users.find_one({"email": email})
        if not user:
            return self.write_json({"error": "Credenziali errate"}, 401)

        if not bcrypt.checkpw(password.encode(), user["password"]):
            return self.write_json({"error": "Credenziali errate"}, 401)

        user_data = {
            "id": str(user["_id"]),
            "email": user["email"]
        }

        self.set_secure_cookie("user", tornado.escape.json_encode(user_data))
        return self.write_json({"message": "Login effettuato", "user": user_data})


class LogoutHandler(BaseHandler):
    async def post(self):
        self.clear_cookie("user")
        return self.write_json({"message": "Logout effettuato"})
