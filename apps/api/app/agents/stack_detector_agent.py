from app.services.stack_service import (
    StackService
)


class StackDetectorAgent:

    def run(
        self,
        repository_path
    ):
        return StackService.detect_stack(
            repository_path
        )