import pickle
from typing import Optional, cast

import aiosqlite
from langgraph.checkpoint.base import Checkpoint, RunnableConfig
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from gaia.domain.planning.planning_session import PlanningSession
from gaia.domain.planning.planning_session_repository import PlanningSessionRepository


class LangGraphPlanningSessionRepository(PlanningSessionRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        self._saver: Optional[AsyncSqliteSaver] = None

    async def initialize(self) -> None:
        self._conn = await aiosqlite.connect(self._db_path)
        self._saver = AsyncSqliteSaver(self._conn)
        await self._saver.setup()

    async def save(self, session: PlanningSession) -> None:
        if not self._saver:
            raise RuntimeError("Repository not initialized")
        config = cast(
            RunnableConfig,
            {"configurable": {"thread_id": session.session_id, "checkpoint_ns": ""}},
        )
        checkpoint = cast(
            Checkpoint,
            {
                "v": 1,
                "id": session.session_id,
                "ts": "",
                "channel_values": {"session_data": pickle.dumps(session)},
                "channel_versions": {},
                "versions_seen": {},
            },
        )
        await self._saver.aput(config, checkpoint, {}, {})

    async def get(self, session_id: str) -> Optional[PlanningSession]:
        if not self._saver:
            raise RuntimeError("Repository not initialized")
        config = cast(
            RunnableConfig,
            {"configurable": {"thread_id": session_id, "checkpoint_ns": ""}},
        )
        checkpoint_tuple = await self._saver.aget_tuple(config)

        if not checkpoint_tuple:
            return None

        checkpoint = checkpoint_tuple.checkpoint
        channel_values = checkpoint.get("channel_values", {})
        if "session_data" in channel_values:
            return pickle.loads(channel_values["session_data"])
        return None
