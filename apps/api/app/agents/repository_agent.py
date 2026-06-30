import os

class RepositoryAgent:

    def analyze(
        self,
        repository_path: str
    ):

        result: dict[str, list[str]] = {
            "files": [],
            "languages": []
        }

        for root, _, files in os.walk(
            repository_path
        ):

            for file in files:

                result["files"].append(
                    os.path.join(root, file)
                )

                if file.endswith(".py"):
                    result["languages"].append(
                        "python"
                    )

                if file.endswith(".js"):
                    result["languages"].append(
                        "javascript"
                    )

        result["languages"] = list(
            set(result["languages"])
        )

        return result