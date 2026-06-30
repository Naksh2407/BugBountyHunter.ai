import os
import shutil
import re
from git import Repo

def parse_repo_owner_name(url: str) -> tuple[str, str] | None:
    # Match https://github.com/owner/repo or git@github.com:owner/repo.git
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?", url)
    if match:
        return match.group(1), match.group(2)
    return None

class GithubService:

    REPO_DIR = "repositories"

    @staticmethod
    def _remove_readonly(func, path, excinfo):
        import stat
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    @classmethod
    def clone_repository(
        cls,
        repo_url: str
    ) -> str:

        os.makedirs(
            cls.REPO_DIR,
            exist_ok=True
        )

        # Normalize slashes first to handle Windows/Unix paths, and strip trailing slashes
        normalized_url = repo_url.replace("\\", "/").rstrip("/")
        repo_name = normalized_url.split("/")[-1]

        target_path = os.path.join(
            cls.REPO_DIR,
            repo_name
        )

        if os.path.exists(target_path):
            shutil.rmtree(target_path, onerror=cls._remove_readonly)

        Repo.clone_from(
            repo_url,
            target_path
        )

        return target_path


    @classmethod
    def create_branch(
        cls,
        repo_path: str,
        branch_name: str
    ):
        repo = Repo(repo_path)
        try:
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
        except Exception:
            # Branch might exist, checkout existing
            repo.git.checkout(branch_name)
        print(f"Checked out branch {branch_name}")

    @classmethod
    def commit_changes(
        cls,
        repo_path: str,
        message: str
    ):
        repo = Repo(repo_path)
        repo.git.add(A=True)  # Stage all changes
        commit = repo.index.commit(message)
        print(f"Committed changes: {commit.hexsha}")

    @classmethod
    def push_branch(
        cls,
        repo_path: str,
        branch_name: str
    ):
        from app.core.config import settings
        token = settings.GITHUB_TOKEN
        repo = Repo(repo_path)
        
        remote = repo.remote()
        url = remote.url
        
        if token:
            parsed = parse_repo_owner_name(url)
            if parsed:
                owner, name = parsed
                url = f"https://x-access-token:{token}@github.com/{owner}/{name}.git"
        else:
            print("Warning: GITHUB_TOKEN is not configured. Pushing changes might require authentication.")

        try:
            repo.git.remote("set-url", "origin", url)
            refspec = f"refs/heads/{branch_name}:refs/heads/{branch_name}"
            remote.push(refspec=refspec, force=True)
            print(f"Pushed branch {branch_name} to remote successfully.")
            return True
        except Exception as e:
            print(f"Error pushing branch to remote: {e}")
            return False

    @classmethod
    def create_pull_request(
        cls,
        repo_url: str,
        branch_name: str,
        title: str,
        body: str
    ):
        from app.core.config import settings
        import httpx
        
        token = settings.GITHUB_TOKEN
        if not token:
            print("No GITHUB_TOKEN configured. Cannot create pull request.")
            return None
            
        parsed = parse_repo_owner_name(repo_url)
        if not parsed:
            print(f"Could not parse owner and repo name from {repo_url}")
            return None
            
        owner, repo = parsed
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        payload = {
            "title": title,
            "body": body,
            "head": branch_name,
            "base": "main"
        }
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        
        try:
            r = httpx.post(url, json=payload, headers=headers)
            if r.status_code == 201:
                return r.json()
            elif r.status_code == 422: # Base branch might be master instead of main
                payload["base"] = "master"
                r2 = httpx.post(url, json=payload, headers=headers)
                if r2.status_code == 201:
                    return r2.json()
            print(f"GitHub API PR creation failed: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"Error calling GitHub API: {e}")
        return None