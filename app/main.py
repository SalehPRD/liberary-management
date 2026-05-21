from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import json
from pathlib import Path
from app.routes import books, members

app = FastAPI(title="Library Management System")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(books.router, prefix="/books")
app.include_router(members.router, prefix="/members")

# Helper functions
def load_books():
    with open("books.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_members():
    with open("members.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Dashboard route
@app.get("/")
def dashboard(request: Request):
    books_list = load_books()
    members_list = load_members()

    total_books = len(books_list)
    borrowed_books = sum(1 for b in books_list if b["is_borrowed"])
    available_books = total_books - borrowed_books
    total_members = len(members_list)
    unique_authors = len(set(b["author"] for b in books_list))

    oldest_book = min(books_list, key=lambda b: b["year"]) if books_list else None
    newest_book = max(books_list, key=lambda b: b["year"]) if books_list else None

    return templates.TemplateResponse(request, "landing.html", {
        "total_books": total_books,
        "borrowed_books": borrowed_books,
        "available_books": available_books,
        "total_members": total_members,
        "unique_authors": unique_authors,
        "oldest_book": oldest_book,
        "newest_book": newest_book,
    })

