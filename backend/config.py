from dotenv import load_dotenv
import os
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
try:
    SESSION_EXPIRE_MINUTES = int(os.getenv('SESSION_EXPIRE_MINUTES', 30))
except ValueError as e:
    SESSION_EXPIRE_MINUTES = 30
    
STRAPI_END_POINT = os.getenv('STRAPI_END_POINT', None)