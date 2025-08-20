# services/openai_config.py
import os
from pydantic_ai.models.openai import OpenAIModel #Integrates pydantic-ai with OpenAI
from pydantic_ai.providers.openai import OpenAIProvider #Provider for OpenAI models
from openai import AsyncAzureOpenAI #SDK to connect to Azure

AZURE_CLIENT = None
OPENAI_MODEL = None

def get_azure_openai_model():
    """Get or create Azure OpenAI model instance"""
    # global AZURE_CLIENT, OPENAI_MODEL
    return AZURE_CLIENT

async def create_azure_openai_model():
    """Create Azure OpenAI model using proper pydantic-ai configuration"""
    print("🔧 Setting up Azure OpenAI with pydantic-ai...")

    global OPENAI_MODEL

    try:
        # Load environment variables (ensure python-dotenv is installed and .env file exists)
        AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
        AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
        AZURE_API_KEY = os.getenv("AZURE_API_KEY")
        AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

        if not all([AZURE_ENDPOINT, AZURE_DEPLOYMENT, AZURE_API_KEY, AZURE_API_VERSION]):
            raise ValueError("One or more Azure OpenAI environment variables are not set.")

        azure_client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_version=AZURE_API_VERSION,
            api_key=AZURE_API_KEY,
            timeout = 120.0
        )

        provider = OpenAIProvider(openai_client=azure_client)
        model = OpenAIModel(
            model_name=AZURE_DEPLOYMENT,
            provider=provider
        )

        print("✅ Model created successfully!")
        return model

    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return None
    

async def create_azure_openai_client():
    """Create and return a raw Azure OpenAI async client"""
    print("🔧 Creating raw Azure OpenAI client...")

    global AZURE_CLIENT

    try:
        AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
        AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
        AZURE_API_KEY = os.getenv("AZURE_API_KEY")

        if not all([AZURE_ENDPOINT, AZURE_API_VERSION, AZURE_API_KEY]):
            raise ValueError("Missing Azure OpenAI credentials for client creation.")

        AZURE_CLIENT = AsyncAzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_version=AZURE_API_VERSION,
            api_key=AZURE_API_KEY,
            timeout=120.0
        )

        print("✅ Raw Azure OpenAI client created successfully!")
        return AZURE_CLIENT

    except Exception as e:
        print(f"❌ Failed to create Azure OpenAI client: {e}")
        return None