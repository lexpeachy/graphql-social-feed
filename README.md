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
- **Testing Playground:** GraphiQL / Apollo Sandbox
- **Deployment:** Render / Railway / Heroku
- **Optional Enhancements:** Redis (caching), Django Channels (real-time subscriptions)

---

## 📊 Example GraphQL Queries

**Fetch posts**
```graphql
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
