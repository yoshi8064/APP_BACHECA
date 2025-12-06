import tornado.escape
from bson import ObjectId
from backend.db import tasks
from backend.db import users
from backend.handlers.auth import BaseHandler
import time
import datetime

class TasksHandler(BaseHandler):
    async def get(self):
        user = self.get_current_user()
        if not user:
            return self.write_json({"error": "Non autenticato"}, 401)

        cursor = tasks.find()
        out = []
        async for t in cursor:
            usr_mail = tasks.find_one({"_id":ObjectId(t["_id"])})
            usr_mail = usr_mail["email"]
            out.append({
                "id": str(t["_id"]),
                "text": f"{  str(datetime.datetime.now())  }\n{usr_mail}\n{  t['text']  }",
                "done": t["done"],
            })
            print(datetime.datetime.now(), user)
            
        return self.write_json({"items": out})

    async def post(self):
        user = self.get_current_user()
        if not user:
            return self.write_json({"error": "Non autenticato"}, 401)

        body = tornado.escape.json_decode(self.request.body)
        text = body.get("text", "").strip()

        if not text:
            return self.write_json({"error": "Testo obbligatorio"}, 400)

        result = await tasks.insert_one({
            "user_id": ObjectId(user["id"]),
            "text": text,
            "done": False
        })

        return self.write_json({"id": str(result.inserted_id)}, 201)


class TaskUpdateHandler(BaseHandler):
    async def put(self, task_id):
        user = self.get_current_user()
        if not user:
            return self.write_json({"error": "Non autenticato"}, 401)

        body = tornado.escape.json_decode(self.request.body)
        done = body.get("done")

        await tasks.update_one(
            {"_id": ObjectId(task_id), "user_id": ObjectId(user["id"])},
            {"$set": {"done": bool(done)}}
        )

        return self.write_json({"message": "Aggiornato"})


class TaskDeleteHandler(BaseHandler):
    async def delete(self, task_id):
        user = self.get_current_user()
        if not user:
            return self.write_json({"error": "Non autenticato"}, 401)

        await tasks.delete_one({
            "_id": ObjectId(task_id),
            "user_id": ObjectId(user["id"])
        })

        return self.write_json({"message": "Eliminato"})
