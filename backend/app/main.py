from fastapi import FastAPI

from app.routers import auth, generator, imports, policies, requests, transactions

app = FastAPI(title="U-OIP API")

app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(transactions.router)
app.include_router(policies.router)
app.include_router(imports.router)
app.include_router(generator.router)


@app.get("/health")
def health():
    return {"ok": True}
