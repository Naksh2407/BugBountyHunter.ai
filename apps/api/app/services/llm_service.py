import os
from openai import OpenAI

class LLMService:
    # Day 5 Observability: Track total token usage dynamically across execution
    total_tokens_used = 0

    @classmethod
    def reset_tokens(cls):
        cls.total_tokens_used = 0

    @classmethod
    def _get_client_and_model(cls) -> tuple[OpenAI | None, str | None]:
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        openai_api_key = os.environ.get("OPENAI_API_KEY")

        if gemini_api_key:
            # Route to Google Gemini via its OpenAI compatibility endpoint
            model = os.environ.get("GEMINI_MODEL") or os.environ.get("OPENAI_MODEL") or "gemini-2.5-flash"
            client = OpenAI(
                api_key=gemini_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            return client, model
        elif openai_api_key:
            model = os.environ.get("OPENAI_MODEL") or "gpt-4o"
            client = OpenAI(api_key=openai_api_key)
            return client, model
        
        return None, None

    @classmethod
    def generate_fix(
        cls,
        issue,
        code_context,
        header_context=None
    ):
        client, model = cls._get_client_and_model()

        if not client:
            print("Using Mock LLM Fallback (No GEMINI_API_KEY or OPENAI_API_KEY configured)")
            cls.total_tokens_used += 420  # Mock token usage
            if "undefined_variable" in code_context:
                return code_context.replace("undefined_variable", "broken_var")
            if "division_by_zero_error" in code_context:
                return code_context.replace("division_by_zero_error", "0.0")
            if "def multiply" in code_context and "res = a * b" in code_context:
                return code_context + "\n    return res"
            return code_context

        try:
            prompt = f"""
You are an expert software engineer.
"""
            if header_context:
                prompt += f"""
Here is the module imports and header context from the file:
{header_context}
"""
            prompt += f"""
Issue:
 
{issue.message}
 
File:
{issue.file_path}
 
Code to fix:
 
{code_context}
 
Return ONLY the corrected code for the specified 'Code to fix' block.
"""

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            if response.usage:
                cls.total_tokens_used += response.usage.total_tokens

            return (
                response
                .choices[0]
                .message
                .content
            )
        except Exception as e:
            print(f"Error calling LLM API in generate_fix: {e}")
            cls.total_tokens_used += 100
            return code_context

    @classmethod
    def generate_refined_fix(
        cls,
        issue,
        code_context,
        failed_code,
        error_message,
        header_context=None
    ):
        client, model = cls._get_client_and_model()

        if not client:
            print("Using Mock LLM Fallback for Refinement")
            cls.total_tokens_used += 650  # Mock token usage
            if "broken_var" in failed_code:
                return failed_code.replace("broken_var", "syntax_error_var = ")
            if "syntax_error_var" in failed_code:
                return failed_code.replace(" + syntax_error_var = ", "")
            if "undefined_variable" in code_context:
                return code_context.replace(" + undefined_variable", "")
            return code_context

        try:
            prompt = f"""
You are an expert software engineer.
"""
            if header_context:
                prompt += f"""
Here is the module imports and header context from the file:
{header_context}
"""
            prompt += f"""
We tried to patch the code to fix the following issue:
{issue.message}
 
Here is the original code context:
{code_context}
 
We generated this replacement candidate code:
{failed_code}
 
However, when running validation, it failed with the following error:
{error_message}
 
Please analyze the error message and the code replacement, and generate a new, corrected replacement code that fixes the issue AND resolves the validation error.
 
Return ONLY the corrected replacement code for the block. No explanations, no markdown blocks.
"""

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            if response.usage:
                cls.total_tokens_used += response.usage.total_tokens

            return (
                response
                .choices[0]
                .message
                .content
            )
        except Exception as e:
            print(f"Error calling LLM API in generate_refined_fix: {e}")
            cls.total_tokens_used += 150
            return failed_code