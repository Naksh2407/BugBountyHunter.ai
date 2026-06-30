class GitService:

    @staticmethod
    def apply_fix(
        file_path,
        fixed_code
    ):

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(fixed_code)