import os
from notebook.auth import passwd

c = get_config()  # noqa

c.NotebookApp.allow_origin = '*'
c.NotebookApp.trust_xheaders = True
c.NotebookApp.port = int(os.getenv(
    "JUPYTER_PORT", "8888"))
c.NotebookApp.password = passwd(os.getenv(
    "JUPYTER_PASS", "admin"))
