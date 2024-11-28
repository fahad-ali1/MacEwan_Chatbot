import os
import uvicorn
from app import app 

# Run the FastAPI app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6584))
    uvicorn.run(app, host="0.0.0.0", port=port)
