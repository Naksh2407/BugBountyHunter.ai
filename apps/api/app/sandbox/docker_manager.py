try:
    import docker  # type: ignore
except ImportError:
    docker = None  # type: ignore

class DockerManager:

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if docker is None:
            raise RuntimeError("The 'docker' python package is not installed. Please install it using 'pip install docker'.")
        if self._client is None:
            self._client = docker.from_env()
        return self._client


    def create_container(
        self,
        image,
        repo_path
    ):

        container = self.client.containers.run(
            image=image,
            detach=True,
            working_dir="/workspace",
            volumes={
                repo_path: {
                    "bind": "/workspace",
                    "mode": "rw"
                }
            },
            mem_limit="2g",
            cpu_period=100000,
            cpu_quota=100000,
            network_disabled=True
        )

        return container