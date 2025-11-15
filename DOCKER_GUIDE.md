# Docker Setup & Commands for FreshTrack

## 1️⃣ Install Docker Desktop

### Windows:
1. Download: https://www.docker.com/products/docker-desktop
2. Run installer
3. Restart computer
4. Verify: `docker --version`

---

## 2️⃣ Build Docker Image

```bash
cd c:\Users\sojib\Music\Website\freshtrack
docker build -t sojib1233/freshtrack:latest .
```

Output will show:
```
Step 1/10 : FROM python:3.13-slim
...
Successfully tagged sojib1233/freshtrack:latest
```

---

## 3️⃣ Run Locally with Docker Compose

```bash
docker-compose up -d
```

This will:
- ✅ Create PostgreSQL database
- ✅ Build Django app
- ✅ Run migrations
- ✅ Collect static files
- ✅ Start on http://localhost:8000

Check logs:
```bash
docker-compose logs -f web
```

Stop containers:
```bash
docker-compose down
```

---

## 4️⃣ Push to Docker Hub

### First time setup:
```bash
docker login
# Enter your Docker Hub username and password
```

### Push image:
```bash
docker tag sojib1233/freshtrack:latest sojib1233/freshtrack:latest
docker push sojib1233/freshtrack:latest
```

View on Docker Hub:
```
https://hub.docker.com/r/sojib1233/freshtrack
```

---

## 5️⃣ Docker Cloud Builder (Docker Buildx)

### Create cloud builder:
```bash
docker buildx create --name cloud-builder --driver cloud sojib1233/freshtrack
docker buildx use cloud-builder
```

### Build for multiple platforms:
```bash
docker buildx build --push -t sojib1233/freshtrack:latest \
  --platform linux/amd64,linux/arm64 .
```

### Build locally:
```bash
docker buildx build -t sojib1233/freshtrack:latest --load .
```

---

## 6️⃣ Run Container

### With environment variables:
```bash
docker run -d \
  -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  --name freshtrack \
  sojib1233/freshtrack:latest
```

### View running containers:
```bash
docker ps
```

### View logs:
```bash
docker logs -f freshtrack
```

### Stop container:
```bash
docker stop freshtrack
```

---

## 7️⃣ Docker Compose (Recommended for Development)

```bash
# Start all services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild images
docker-compose up -d --build

# Remove volumes (data)
docker-compose down -v
```

---

## 📋 Environment Variables (.env)

```
DEBUG=False
SECRET_KEY=django-insecure-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DATABASE_URL=postgresql://freshtrack_user:freshtrack_password@db:5432/freshtrack_db
```

---

## ✅ Verify Deployment

```bash
# Check if app is running
curl http://localhost:8000

# Enter container
docker exec -it freshtrack bash

# Run migrations inside container
docker exec -it freshtrack python manage.py migrate

# Create superuser
docker exec -it freshtrack python manage.py createsuperuser
```

---

## 🐛 Troubleshooting

### Port already in use:
```bash
docker-compose down
# or use different port
docker run -p 8001:8000 sojib1233/freshtrack:latest
```

### Clear everything:
```bash
docker-compose down -v
docker system prune -a
```

### View image size:
```bash
docker images | grep freshtrack
```

### Inspect container:
```bash
docker inspect freshtrack
```

---

## 📊 Production Checklist

- [ ] Change DEBUG to False
- [ ] Set strong SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Use PostgreSQL (not SQLite)
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Use reverse proxy (nginx)

---

**All set! Your FreshTrack app is Dockerized and ready to deploy!** 🚀
