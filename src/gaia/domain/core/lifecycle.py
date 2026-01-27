import logging
from typing import Awaitable, Callable, List

logger = logging.getLogger(__name__)

ShutdownHook = Callable[[], Awaitable[None]]


class AppLifecycleManager:
    def __init__(self):
        self._shutdown_hooks: List[ShutdownHook] = []

    def register_shutdown_hook(self, hook: ShutdownHook) -> None:
        """Register an async function to be called on shutdown."""
        self._shutdown_hooks.append(hook)

    async def shutdown(self) -> None:
        """Execute all registered shutdown hooks in reverse order."""
        for hook in reversed(self._shutdown_hooks):
            try:
                await hook()
            except Exception as e:
                logger.error(f"Error during shutdown hook: {e}", exc_info=True)
