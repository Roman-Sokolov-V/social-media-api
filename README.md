# social-media-api
 RESTful API for a social media platform. The API allow users to create profiles, follow other users, create and retrieve posts, manage likes and comments, and perform basic social media actions.

### Technologies to use:
1. Python, Django, Django, REST
2. Docker
3. Celery
4. Redis


### How to run
- Clone project: `git clone https://github.com/Roman-Sokolov-V/social-media-api.git`
- go to project path: `cd <project_directory>`
- Create venv: `python -m venv venv`
- Activate it: `venv\scripts\activate`
- Install requirements: `pip install -r requirements.txt`
- Run migrations: `python manage.py makemigrations`
- Run Redis: `docker run -d -p 6379:6379 redis`
- Run Celery for tasks handling: `celery -A api_config worker --loglevel=INFO --pool=solo`
- Run app: `python manage.py runserver`

### API Endpoints
- POST /api/register/: Register a new user
- POST /api/login/: Log in to get the authentication token
- POST /api/logout/: Log out and invalidate the token
- GET /api/profile/: List users profiles with optional filters (user id, 
  username, first name, last name)
- GET /api/profile/{id}/: Retrieve a user profile by user id
- PUT /api/profile/{id}/: Update a user profile
- GET /api/post/: List all posts, with optional filters (by hashtags, 
  author, content)
- POST /api/post/: Create a new post
- GET /api/post/{id}/: Retrieve a single post by ID
- PUT /api/post/{id}/: Update post
- EXTRA /api/post/{id}/upload_image/: add image to post
- EXTRA /api/post/{id}/like/: like / unlike post
- EXTRA /api/post/liked/: list posts that you likes
- DELETE /api/post/{id}/: Delete post
- POST /api/comment/: Add a comment to a post
- GET /api/comment/: List comments
- POST /api/comment/: Add a like to a post
- GET /api/comment/: List likes
- GET /api/following/: List of following
- GET /api/follow/: List of your follow 
- POST /api/follow/: Create follow
- GET /api/follow/{id}/: Retrieve a single follow by ID 
- DELETE GET /api/follow/{id}/: Unfollow

### Documentation
The API is documented using Swagger/OpenAPI, Redoc/OpenAPI and you can access 
the documentation at the 
- api/schema/swagger/
- api/schema/redoc/ 


### License
This project is licensed under the MIT License - see the LICENSE file for details.