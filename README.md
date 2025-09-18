# GraphQL Social Feed Backend

A **scalable social media feed backend** built with **Django, PostgreSQL, and GraphQL (Graphene-Django)**.  
This project simulates the backend of a social media platform, focusing on **flexible querying, real-time interactions, and high-performance database design**.

---

## 🚀 Features

- **User Management**
  - Sign up, log in (JWT authentication)
  - User profiles with role-based permissions

- **Post Management**
  - Create, edit, delete, and fetch posts
  - Attach comments, likes, and shares

- **Interactions**
  - Like, comment, and share posts
  - Track interaction counts per post
  - Analytics queries for popular posts & active users

- **GraphQL API**
  - Flexible queries & mutations using Graphene-Django
  - Playground for interactive API testing
  - Relay-style pagination for scalable feeds

- **Feed System**
  - Personalized feed (posts from followed users)
  - Trending posts (based on interactions)

- **Real-Time (Bonus)**
  - GraphQL subscriptions for new posts and interactions

- **Scalability**
  - Optimized queries with `select_related` & `prefetch_related`
  - Indexing in PostgreSQL for high-volume interactions

---

## 🛠️ Tech Stack

- **Backend:** Django, Graphene-Django  
- **Database:** PostgreSQL  
- **Auth:** JWT (via `django-graphql-jwt`)  
- **Testing Playground:** /GraphiQL
- **Deployment:** Render
- **Optional Enhancements:** Redis (caching), Django Channels (real-time subscriptions)  

---

## ⚙️ Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lexpeachy/graphql-social-feed.git
   cd config

Create and activate a virtual environment

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


Install dependencies

pip install -r requirements.txt


Configure environment variables
Copy the example file and update with your values:

cp .env.example .env


Run migrations & create superuser

python manage.py migrate
python manage.py createsuperuser


Start the development server

python manage.py runserver


Now open http://localhost:8000/graphql/
 to access GraphQL Playground.

🔑 Environment Variables

Your .env file should include:

SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/socialdb
ALLOWED_HOSTS=127.0.0.1,localhost

📊 Example GraphQL Queries

Fetch posts

query {
  posts(limit: 5, orderBy: "-created_at") {
    id
    content
    author {
      username
    }
    likesCount
    comments {
      id
      text
      user {
        username
      }
    }
  }
}

✨ Example Mutations

Sign up

mutation {
  register(username: "lex", email: "lex@example.com", password: "password123") {
    user {
      id
      username
      email
    }
  }
}


Login (JWT)

mutation {
  tokenAuth(username: "lex", password: "password123") {
    token
  }
}


Create Post

mutation {
  createPost(content: "This is my first post!") {
    post {
      id
      content
      author {
        username
      }
    }
  }
}


Like Post

mutation {
  likePost(postId: 1) {
    success
    post {
      id
      likesCount
    }
  }
}

🧪 Running Tests

Run unit tests with:

pytest
# or
python manage.py test


Generate coverage report:

coverage run -m pytest
coverage html

📂 Version Control Workflow

For version control I directly pushed to main since I was alone and I tested my codes before pushing the code.

You can use a simple branching strategy:

main → stable, production-ready code

dev → active development branch

feature/* → individual features/fixes

Commit message format:

feat: set up Django project with PostgreSQL
feat: create models for posts, comments, and interactions
feat: implement GraphQL API for querying posts and interactions
feat: integrate and publish GraphQL Playground
perf: optimize database queries for interactions
docs: update README with API usage
docs: update README with setup instructions

🚀 Deployment 

Render:

Set DATABASE_URL and SECRET_KEY in environment.

Run migrations:

python manage.py migrate


Start server (example with Gunicorn):

gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
