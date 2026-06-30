import os


class StackService:

    @staticmethod
    def detect_stack(path):

        files = os.listdir(path)

        if "package.json" in files:
            return "node"

        if "requirements.txt" in files:
            return "python"

        if "pom.xml" in files:
            return "java"

        if "Cargo.toml" in files:
            return "rust"

        if "go.mod" in files:
            return "go"

        return "unknown"