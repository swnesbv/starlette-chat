from starlette.routing import Mount

from channel.urls import routes as chat_routes
from collocutor.urls import routes as collocutor_routes
from participant.urls import routes as participant_routes
from account.urls import routes as account_routes
from auth_privileged.urls import routes as privileged_routes
# ..
from sitemap.urls import routes as sitemap_routes


routes = [
    # ..
    Mount("/account", routes=account_routes),
    Mount("/privileged", routes=privileged_routes),
    Mount("/chat", routes=chat_routes),
    Mount("/collocutor", routes=collocutor_routes),
    Mount("/participant", routes=participant_routes),
    # ..
    Mount("/sitemap", routes=sitemap_routes),

]
