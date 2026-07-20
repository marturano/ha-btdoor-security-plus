from custom_components.btdoor_security_plus.dialog import (
    DialogEngine,
    DialogState,
    DialogTransitionError,
)


def test_complete_dialog_lifecycle() -> None:
    engine = DialogEngine()
    session = engine.receive_invite("call-1", remote_tag="remote")
    assert session.state is DialogState.INVITE_RECEIVED
    for state in (
        DialogState.EARLY_DIALOG,
        DialogState.READY_TO_ANSWER,
        DialogState.WAITING_ACK,
        DialogState.ESTABLISHED,
        DialogState.TERMINATED,
    ):
        session = engine.transition("call-1", state)
    assert session.state is DialogState.TERMINATED
    assert engine.diagnostics()["active_count"] == 0


def test_invalid_dialog_transition() -> None:
    engine = DialogEngine()
    engine.receive_invite("call-2")
    try:
        engine.transition("call-2", DialogState.ESTABLISHED)
    except DialogTransitionError:
        pass
    else:
        raise AssertionError("invalid transition was accepted")
