from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import match_router, overview_router, player_router, standing_router

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://stony-brook-fc-web.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(player_router.router)
app.include_router(match_router.router)
app.include_router(standing_router.router)
app.include_router(overview_router.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
