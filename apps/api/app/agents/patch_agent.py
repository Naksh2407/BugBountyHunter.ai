from app.services.patch_service import (
    PatchService
)


class PatchAgent:

    @staticmethod
    def create_patch(
        file_path,
        fixed_code
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            original = f.read()

        return PatchService.generate_patch(
            original,
            fixed_code
        )