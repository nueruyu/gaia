import pickle
from typing import Optional, cast

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.base import Checkpoint, RunnableConfig

from gaia.domain.aggregates import PlanningSession
from gaia.domain.repositories import PlanningSessionRepository


class LangGraphRepository(PlanningSessionRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._saver: Optional[AsyncSqliteSaver] = None

    async def initialize(self) -> None:
        conn = AsyncSqliteSaver.from_conn_string(self._db_path)
        self._saver = await conn.__aenter__()
        await self._saver.setup()

    async def save(self, session: PlanningSession) -> None:
        if not self._saver:
            raise RuntimeError("Repository not initialized")
        config = cast(RunnableConfig, {"configurable": {"thread_id": session.session_id}})
        checkpoint = cast(Checkpoint, {
            "v": 1,
            "id": session.session_id,
            "ts": "",
            "channel_values": {"session_data": pickle.dumps(session)},
            "channel_versions": {},
            "versions_seen": {},
        })
        await self._saver.aput(config, checkpoint, {}, {})

    async def get(self, session_id: str) -> Optional[PlanningSession]:
        if not self._saver:
            raise RuntimeError("Repository not initialized")
        config = cast(RunnableConfig, {"configurable": {"thread_id": session_id}})
        checkpoint_tuple = await self._saver.aget_tuple(config)

        if not checkpoint_tuple:
            return None

        checkpoint = checkpoint_tuple.checkpoint
        channel_values = checkpoint.get("channel_values", {})
        if "session_data" in channel_values:
            return pickle.loads(channel_values["session_data"])
        return None
