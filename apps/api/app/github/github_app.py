import hmac
import hashlib
import time

try:
    import jwt  # type: ignore
except ImportError:
    jwt = None  # type: ignore

class GithubApp:

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify GitHub webhook payload signature using HMAC-SHA256.
        No external libraries are required.
        """
        if not secret or not signature:
            return False
        
        # GitHub signature is in format: sha256=HEX_SIGNATURE
        expected = signature.split("=")[-1]
        
        computed = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, computed)

    @staticmethod
    def generate_jwt(app_id: str, private_key_pem: str) -> str:
        """
        Generate JWT for GitHub App authentication using RS256 algorithm.
        Requires 'PyJWT' and 'cryptography' library packages.
        """
        if jwt is None:
            raise RuntimeError("The 'PyJWT' and 'cryptography' python packages are required to generate GitHub App JWTs. Please run 'pip install PyJWT cryptography'.")
            
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),
            "iss": int(app_id)
        }
        
        # GitHub App authentication requires RS256 algorithm
        token = jwt.encode(payload, private_key_pem, algorithm="RS256")
        return token
