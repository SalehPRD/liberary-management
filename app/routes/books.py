from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import json

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def load_books():
    with open("books.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_books(books):
    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

@router.get("/landing")
def books_landing(request: Request):
    books = load_books()
    return templates.TemplateResponse(request, "books_landing.html", {
        "books": books
    })

@router.get("/add")
def add_book_form(request: Request):
    return templates.TemplateResponse(request, "book_form.html", {
        "action": "add",
        "book": None,
        "error": None
    })

@router.post("/")
def create_book(
    request: Request,
    isbn: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    is_borrowed: str = Form("false")
):
    books = load_books()
    if any(b["isbn"] == isbn for b in books):
        return templates.TemplateResponse(request, "book_form.html", {
            "action": "add",
            "book": None,
            "error": "این شابک قبلاً ثبت شده است!"
        })
    books.append({
        "isbn": isbn,
        "title": title,
        "author": author,
        "year": year,
        "is_borrowed": is_borrowed == "true"
    })
    save_books(books)
    return RedirectResponse(url="/books/landing", status_code=303)

@router.get("/edit/{isbn}")
def edit_book_form(request: Request, isbn: str):
    books = load_books()
    book = next((b for b in books if b["isbn"] == isbn), None)
    return templates.TemplateResponse(request, "book_form.html", {
        "action": "edit",
        "book": book,
        "error": None
    })

@router.post("/{isbn}")
def update_book(
    request: Request,
    isbn: str,
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    is_borrowed: str = Form("false")
):
    books = load_books()
    for b in books:
        if b["isbn"] == isbn:
            b["title"] = title
            b["author"] = author
            b["year"] = year
            b["is_borrowed"] = is_borrowed == "true"
            break
    save_books(books)
    return RedirectResponse(url="/books/landing", status_code=303)

@router.get("/delete/{isbn}")
def delete_book_confirm(request: Request, isbn: str):
    books = load_books()
    book = next((b for b in books if b["isbn"] == isbn), None)
    return templates.TemplateResponse(request, "book_delete.html", {
        "book": book
    })

@router.post("/delete/{isbn}")
def delete_book(isbn: str):
    books = load_books()
    books = [b for b in books if b["isbn"] != isbn]
    save_books(books)
    return RedirectResponse(url="/books/landing", status_code=303)
