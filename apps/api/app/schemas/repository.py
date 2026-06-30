from pydantic import BaseModel


class RepositoryCreate(BaseModel):
    github_url: str


class RepositoryResponse(BaseModel):
    id: str
    github_url: str
    repo_name: str
    status: str

    class Config:
        from_attributes = True