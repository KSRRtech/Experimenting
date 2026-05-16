"""Auto-generated FastAPI application — new endpoint added daily."""
from fastapi import FastAPI

app = FastAPI(
    title="KSRRtech Experimenting API",
    description="Daily auto-generated public REST API endpoints powered by Claude.",
    version="1.0.0",
)


@app.get("/", tags=["root"])
def root():
    """API index — lists available route prefixes."""
    return {
        "message": "Welcome to KSRRtech Experimenting API",
        "docs": "/docs",
        "total_route_modules": 0,
    }
