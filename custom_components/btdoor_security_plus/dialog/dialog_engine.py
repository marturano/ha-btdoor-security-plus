"""Deterministic SIP dialog state machine."""

from __future__ import annotations

from datetime import UTC, datetime

from .dialog_session import DialogSession
from .dialog_state import DialogState


class DialogTransitionError(RuntimeError):
    """Raised when a transition violates the dialog lifecycle."""


_ALLOWED: dict[DialogState, frozenset[DialogState]] = {
    DialogState.IDLE: frozenset({DialogState.INVITE_RECEIVED}),
    DialogState.INVITE_RECEIVED: frozenset({DialogState.EARLY_DIALOG, DialogState.TERMINATED}),
    DialogState.EARLY_DIALOG: frozenset({DialogState.READY_TO_ANSWER, DialogState.TERMINATED}),
    DialogState.READY_TO_ANSWER: frozenset({DialogState.WAITING_ACK, DialogState.TERMINATED}),
    DialogState.WAITING_ACK: frozenset({DialogState.ESTABLISHED, DialogState.TERMINATED}),
    DialogState.ESTABLISHED: frozenset({DialogState.TERMINATED}),
    DialogState.TERMINATED: frozenset(),
}


class DialogEngine:
    """Own and validate active SIP dialog sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, DialogSession] = {}

    def receive_invite(self, call_id: str, *, remote_tag: str | None = None) -> DialogSession:
        if (
            call_id in self._sessions
            and self._sessions[call_id].state is not DialogState.TERMINATED
        ):
            raise DialogTransitionError(f"Active dialog already exists for {call_id}")
        session = DialogSession(call_id=call_id, remote_tag=remote_tag)
        self._sessions[call_id] = session
        return self.transition(call_id, DialogState.INVITE_RECEIVED)

    def transition(self, call_id: str, target: DialogState) -> DialogSession:
        try:
            session = self._sessions[call_id]
        except KeyError as err:
            raise DialogTransitionError(f"Unknown dialog {call_id}") from err
        if target not in _ALLOWED[session.state]:
            raise DialogTransitionError(f"Invalid transition {session.state} -> {target}")
        session.state = target
        session.updated_at = datetime.now(UTC)
        return session

    def get(self, call_id: str) -> DialogSession | None:
        return self._sessions.get(call_id)

    def terminate(self, call_id: str) -> DialogSession:
        return self.transition(call_id, DialogState.TERMINATED)

    def diagnostics(self) -> dict[str, object]:
        return {
            "active_count": sum(
                s.state is not DialogState.TERMINATED for s in self._sessions.values()
            ),
            "sessions": [session.snapshot() for session in self._sessions.values()],
        }
