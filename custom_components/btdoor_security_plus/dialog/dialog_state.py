"""SIP dialog states."""

from enum import StrEnum


class DialogState(StrEnum):
    IDLE = "idle"
    INVITE_RECEIVED = "invite_received"
    EARLY_DIALOG = "early_dialog"
    READY_TO_ANSWER = "ready_to_answer"
    WAITING_ACK = "waiting_ack"
    ESTABLISHED = "established"
    TERMINATED = "terminated"
