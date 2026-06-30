import httpx
from app.github.github_app import GithubApp

class PRCreator:

    @staticmethod
    def get_installation_access_token(
        app_id: str,
        private_key_pem: str,
        installation_id: str
    ) -> str | None:
        """
        Request a temporary installation access token from GitHub App.
        This token can be used as GITHUB_TOKEN to push code or create PRs.
        """
        try:
            # 1. Generate JWT
            jwt_token = GithubApp.generate_jwt(app_id, private_key_pem)
            
            # 2. Query access tokens endpoint
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
            
            r = httpx.post(url, headers=headers)
            if r.status_code == 201:
                return r.json().get("token")
            else:
                print(f"Failed to fetch installation access token: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"Error fetching installation access token: {e}")
        return None
