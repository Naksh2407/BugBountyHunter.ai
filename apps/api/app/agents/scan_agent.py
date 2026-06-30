from app.services.scanner_service import (
    PythonScanner,
    NodeScanner
)


class ScanAgent:

    def run(
        self,
        stack,
        path
    ):

        if stack == "python":
            return PythonScanner.scan(path)

        if stack == "node":
            return NodeScanner.scan(path)

        return {
            "error": "unsupported stack"
        }