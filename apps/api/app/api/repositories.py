from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.repository import Repository

from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse
)

router = APIRouter()


@router.post(
    "/repositories",
    response_model=RepositoryResponse
)
def create_repository(
    payload: RepositoryCreate,
    db: Session = Depends(get_db)
):

    repo_name = payload.github_url.split("/")[-1]

    repository = Repository(
        github_url=payload.github_url,
        repo_name=repo_name
    )

    db.add(repository)

    db.commit()

    db.refresh(repository)

    return repository