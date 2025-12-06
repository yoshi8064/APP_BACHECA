import asyncio, tornado

from backend.db import COOKIE_KEY, PORT
from backend.handlers.auth import RegisterHandler, LoginHandler, LogoutHandler
from backend.handlers.tasks import TasksHandler, TaskUpdateHandler, TaskDeleteHandler


def make_app():
    return tornado.web.Application(
        [
            (r"/api/register", RegisterHandler),
            (r"/api/login", LoginHandler),
            (r"/api/logout", LogoutHandler),

            (r"/api/tasks", TasksHandler),
            (r"/api/tasks/([a-f0-9]{24})", TaskUpdateHandler),
            (r"/api/tasks/([a-f0-9]{24})/delete", TaskDeleteHandler),

            (r"/templates/(.*)", tornado.web.StaticFileHandler, {"path": "templates"}),

            (r"/", tornado.web.RedirectHandler, {"url": "/templates/login.html"}),
        ],
        cookie_secret=COOKIE_KEY,
        autoreload=True,
        debug=True
    )


async def main():
    app = make_app()
    app.listen(PORT)
    print(f"Server avviato su http://localhost:{PORT}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer spento.")
    except Exception as e:
        print(f"Errore critico durante l'avvio del server: {e}")
