import uvicorn
from dotenv import load_dotenv

from gaia.containers import Container
from gaia.presentation.api.app import create_app


def main():
    """
    This is the composition root of the application.
    It creates the DI container, wires it to the application layers,
    and starts the web server.
    """
    # 1. Load environment variables from .env file
    load_dotenv()

    # 2. Create the DI container instance
    container = Container()

    # 3. Configure the container using environment variables
    # This sets the LLM_MODE for the Selector provider.
    # It defaults to "MOCK" if the variable is not set.
    container.config.LLM_MODE.from_env("LLM_MODE", "MOCK")

    # 4. Wire the container to the modules that need injection.
    container.wire(modules=["gaia.presentation.api.routers.plan"])

    # 5. Create the FastAPI app instance
    app = create_app()

    # 6. Run the Uvicorn server programmatically
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
