import difflib


class PatchService:

    @staticmethod
    def generate_patch(
        original,
        modified
    ):

        diff = difflib.unified_diff(
            original.splitlines(),
            modified.splitlines(),
            lineterm=""
        )

        return "\n".join(diff)