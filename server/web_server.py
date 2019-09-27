import os

from pathlib import Path

from twisted.web import server, resource, static, http
from twisted.internet import reactor

import server.utils.helper as helper

script_path = Path(os.path.dirname(__file__))
project_root_path = script_path.parent

if __name__ == "__main__":

    port = 8000
    root = resource.Resource()

    rootPage = static.File(os.path.join(project_root_path,"client/index.html"))
    root.putChild(helper.str_to_utf8(''), rootPage)

    client_path = os.path.join(project_root_path, "client/")
    for file in os.listdir(client_path):
            root.putChild(helper.str_to_utf8(file), static.File(client_path + file))

    site = server.Site(root)
    reactor.listenTCP(8000, site)

    print("web server starting on port:", port)
    reactor.run()
