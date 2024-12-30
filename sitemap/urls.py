
from starlette.routing import Route

from sitemap import sitemap


routes = [
    Route(
        "/generate-sitemap",
        sitemap.all_sitemap,
        methods=["GET"]
    )
]
