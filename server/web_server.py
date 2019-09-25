import os

from pathlib import Path

from twisted.web import server, resource, static
from twisted.internet import reactor

file_path = Path(os.path.dirname(__file__))
root_path = file_path.parent

if __name__ == "__main__":

    port = 8000
    root = static.File(bytes(os.path.join(root_path,"client/index.html"),'utf-8'))

    client_dir = os.path.join(root_path, "client/")
    for file in os.listdir(client_dir):
        root.putChild(bytes(file,'utf-8'), static.File(bytes(client_dir + file,'utf-8')))

    site = server.Site(root)
    reactor.listenTCP(8000, site)

    print("web server starting on port:", port)
    reactor.run()
