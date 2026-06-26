class EmergencyStop:
    """Phase 5 placeholder for a global emergency stop hotkey."""

    def __init__(self) -> None:
        self.triggered = False

    def stop(self) -> None:
        self.triggered = True

