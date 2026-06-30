class SandboxRunner:

    @staticmethod
    def execute(
        container,
        command
    ):

        result = container.exec_run(
            command
        )

        return {
            "exit_code": result.exit_code,
            "output": result.output.decode()
        }