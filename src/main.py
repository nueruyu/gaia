from gaia.containers import Container
from gaia.presentation.api.app import create_app

container = Container()

container.wire(modules=["gaia.presentation.api.routers.plan"])

app = create_app()
