from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import json

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def load_members():
    with open("members.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_members(members):
    with open("members.json", "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

def generate_member_id(members):
    if not members:
        return "M001"
    last_id = max(int(m["member_id"][1:]) for m in members)
    return f"M{last_id + 1:03d}"

@router.get("/landing")
def members_landing(
    request: Request,
    search: str = "",
    sort: str = "",
    page: int = 1
):
    members = load_members()

    if search:
        members = [m for m in members if
            search.lower() in m["name"].lower() or
            search.lower() in m["email"].lower() or
            search.lower() in m["member_id"].lower()
        ]

    if sort == "name":
        members = sorted(members, key=lambda m: m["name"])
    elif sort == "email":
        members = sorted(members, key=lambda m: m["email"])

    per_page = 5
    total = len(members)
    total_pages = max(1, (total + per_page - 1) // per_page)
    members = members[(page - 1) * per_page: page * per_page]

    base_url = f"/members/landing?search={search}&sort={sort}"

    return templates.TemplateResponse(request, "members_landing.html", {
        "members": members,
        "search": search,
        "sort": sort,
        "page": page,
        "total_pages": total_pages,
        "base_url": base_url
    })

@router.get("/add")
def add_member_form(request: Request):
    return templates.TemplateResponse(request, "member_form.html", {
        "action": "add",
        "member": None,
        "error": None
    })

@router.post("/")
def create_member(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...)
):
    members = load_members()
    member_id = generate_member_id(members)
    members.append({
        "member_id": member_id,
        "name": name,
        "email": email,
        "phone": phone
    })
    save_members(members)
    return RedirectResponse(url="/members/landing", status_code=303)

@router.get("/edit/{member_id}")
def edit_member_form(request: Request, member_id: str):
    members = load_members()
    member = next((m for m in members if m["member_id"] == member_id), None)
    return templates.TemplateResponse(request, "member_form.html", {
        "action": "edit",
        "member": member,
        "error": None
    })

@router.post("/{member_id}")
def update_member(
    request: Request,
    member_id: str,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...)
):
    members = load_members()
    for m in members:
        if m["member_id"] == member_id:
            m["name"] = name
            m["email"] = email
            m["phone"] = phone
            break
    save_members(members)
    return RedirectResponse(url="/members/landing", status_code=303)

@router.get("/delete/{member_id}")
def delete_member_confirm(request: Request, member_id: str):
    members = load_members()
    member = next((m for m in members if m["member_id"] == member_id), None)
    return templates.TemplateResponse(request, "member_delete.html", {
        "member": member
    })

@router.post("/delete/{member_id}")
def delete_member(member_id: str):
    members = load_members()
    members = [m for m in members if m["member_id"] != member_id]
    save_members(members)
    return RedirectResponse(url="/members/landing", status_code=303)
