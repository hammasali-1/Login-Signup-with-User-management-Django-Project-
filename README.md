# Customer Portal (Django)

## Overview
A modern, responsive Customer Portal built with Django. It provides role-based dashboards, an inbox for contact messages, customer management, and a polished UI with SPA-style navigation and theme persistence.

## Key Features
- Authentication: signup, login, logout
- Roles & permissions: `admin`, `manager`, `user`
- Customers: list, search, status toggle, soft delete, create/update
- Dashboard: real counts for total/active/inactive, responsive table
- Inbox (admin/manager): live updates, view/delete, bulk actions
- Inbox filters: live search by username/email/subject/text; filter by role; custom date/time range
- Stats page: role-aware counts and charts (where applicable)
- Profile: avatar upload/remove, role chip, change password, delete account (user-only)
- Theme: light/dark toggle with per-user persistence and local fallback
- SPA navigation: fast page transitions using link attributes (no full reload)
- Responsive design: mobile-first layout for navbar, dashboard, profile, home page

## Tech Stack
- Backend: Django (5.x), SQLite
- Frontend: Bootstrap 5 via CDN
- Media: Image uploads (avatar) via `ImageField` with dynamic path

## Roles & Access
- Admin: full access — customers, inbox, stats, site info edits
- Manager: limited to `user`-role records in inbox and customer views
- User: profile management, can delete own account; no access to admin/manager tools

## Inbox Workflow
- Live search while typing using `q` across username/email/subject/text
- Filters:
  - Role: `admin` | `manager` | `user`
  - Date/time: `start` and `end` using `YYYY-MM-DD HH:MM` or `YYYY-MM-DDTHH:MM`
- Bulk actions: mark read/unread, resolve/unresolve, delete
- Per-message modal view; opening a modal auto-marks message as read

## UI/UX Highlights
- Modern gradients and glass cards
- Mobile-optimized navbar, dropdowns, and tables
- SPA-like content swaps for fast navigation
- Theme toggle button in navbar with per-user persistence

## Project Structure (selected)
- `pro/myapp/models.py`: `customers`, `ContactMessage`, `SiteInfo`
- `pro/myapp/views.py`: dashboard (`myfile`), inbox, profile, contact/about, stats
- `pro/myapp/urls.py`: routes for all views (inbox data/bulk actions included)
- `pro/templetes/`: Django templates (home, profile, inbox, dashboard, partials/navbar)
- `pro/pro/settings.py`: base settings (templates dir configured)

## Getting Started
1. Create and activate a virtual environment
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies (Django, Pillow)
   ```
   pip install Django Pillow
   ```
3. Apply migrations
   ```
   python manage.py migrate
   ```
4. Run the development server
   ```
   python manage.py runserver
   ```
5. Open `http://127.0.0.1:8000/` and create an account via Signup.

## Configuration Notes
- Media uploads store files under `upload/profile_image/`. Configure `MEDIA_ROOT` and `MEDIA_URL` for production serving.
- SQLite is used by default; adjust `DATABASES` for your environment.

## Development Tips
- Use the navbar links with SPA attributes for smooth transitions.
- Theme toggle persists per user when logged in; otherwise via local storage.
- Manager role is automatically scoped to `user` records across inbox and customer views.

## Screens & Pages
- Home: hero section with CTA, responsive layout
- Dashboard: customer table, counts, search
- Inbox: stats, filters, bulk actions, modals, live polling
- Profile: avatar management, role chip, password change, account delete
- Contact/About: editable content (admin)
- Stats: summarized metrics and visualizations (role-aware)
