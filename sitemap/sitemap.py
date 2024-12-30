import subprocess
from starlette.responses import RedirectResponse


async def all_sitemap(request):
    # ..
    if request.method == "GET":
        # ..
        subprocess.Popen(["./ENV/Scripts/python", "generate_sitemap.py"])
        # ..
        return RedirectResponse(
            "/messages?msg=the request is being processed..", status_code=302
        )
