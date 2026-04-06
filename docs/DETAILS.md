## Project Details

### In this project, the following were implemented:
- Comment model with threaded replies (recursive self-referencing FK)
- Real-time comment broadcasting via Django Channels + Redis channel layer
- CAPTCHA verification on comment submission (django-simple-captcha)
- Image upload with automatic resize to 320×240 (Pillow)
- TXT file upload with 100 KB size limit
- XHTML text validation (allowed tags: `<a>`, `<strong>`, `<i>`, `<code>`) with XSS protection
- Sorting by nickname, email, date and pagination (25 per page)
- Robot avatars generated per email hash via RoboHash
- ORM-level caching with django-cacheops + Redis
- Cloud media storage via Cloudinary
- Static file management with WhiteNoise
- Docker containerization with Docker Compose (PostgreSQL, Redis, Backend, Frontend)
- Unit tests: models, serializers, validators, views, consumers, routing