"""Auto-generated FastAPI application — new endpoint added daily."""
import importlib
import os
from fastapi import FastAPI

app = FastAPI(
    title="KSRRtech Experimenting API",
    description="Daily auto-generated public REST API endpoints powered by Claude.",
    version="1.0.0",
)


@app.get("/", tags=["root"])
def root():
    """API index — lists available route prefixes."""
    routes_dir = os.path.join(os.path.dirname(__file__), "routes")
    modules = sorted(
        f[:-3] for f in os.listdir(routes_dir)
        if f.endswith(".py") and f != "__init__.py"
    )
    return {
        "message": "Welcome to KSRRtech Experimenting API",
        "docs": "/docs",
        "total_route_modules": len(modules),
        "routes": modules,
    }


# Dynamically load every router in api/routes/
_routes_dir = os.path.join(os.path.dirname(__file__), "routes")
for _fname in sorted(os.listdir(_routes_dir)):
    if _fname.endswith(".py") and _fname != "__init__.py":
        _module_name = f"api.routes.{_fname[:-3]}"
        _mod = importlib.import_module(_module_name)
        app.include_router(_mod.router)
