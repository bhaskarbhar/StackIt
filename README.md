# StackIt - A Minimal Q&A Forum Platform

StackIt is a modern, minimal question-and-answer platform built with FastAPI (backend) and React (frontend). It supports collaborative learning and structured knowledge sharing with a focus on simplicity and user experience.

## Features

### Core Features
- **Ask Questions**: Create questions with rich text editor, tags, and formatting
- **Answer Questions**: Post detailed answers with rich text formatting
- **Voting System**: Upvote/downvote questions and answers
- **Accept Answers**: Question owners can mark answers as accepted
- **Tagging System**: Organize content with tags (1-5 tags per question)
- **Search & Filter**: Search questions and filter by tags
- **User Authentication**: Secure JWT-based authentication
- **User Roles**: Guest, User, and Admin roles with different permissions

### Rich Text Editor Features
- Bold, Italic, Strikethrough formatting
- Numbered and bullet lists
- Hyperlink insertion
- Image upload support
- Text alignment options

### Notification System
- Real-time notification bell in navigation
- Notifications for:
  - New answers to your questions
  - Comments on your answers
  - Mentions using @username
- Unread notification count display

### Admin Features
- User management (ban/unban users)
- Content moderation
- Platform statistics
- Question and answer deletion

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database with Motor for async operations
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation and settings management
- **Python 3.8+**: Core programming language

### Frontend
- **React 19**: Modern React with hooks
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Server state management
- **React Hook Form**: Form handling and validation
- **React Quill**: Rich text editor
- **Lucide React**: Icon library
- **React Hot Toast**: Toast notifications

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- MongoDB (local or cloud instance)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd StackIt
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration
1. Copy the environment example file:
```bash
cp env.example .env
```

2. Edit `.env` file with your configuration:
```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=stackit

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# CORS Configuration
FRONTEND_URL=http://localhost:5173
```

#### Start the Backend Server
```bash
python run.py
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Dependencies
```bash
npm install
```

#### Start the Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update user profile

### Questions
- `GET /questions/` - List questions with filtering
- `POST /questions/` - Create new question
- `GET /questions/{id}` - Get question details
- `PUT /questions/{id}` - Update question
- `DELETE /questions/{id}` - Delete question
- `POST /questions/{id}/vote` - Vote on question

### Answers
- `POST /answers/` - Create answer
- `GET /answers/question/{id}` - Get answers for question
- `PUT /answers/{id}` - Update answer
- `DELETE /answers/{id}` - Delete answer
- `POST /answers/{id}/vote` - Vote on answer
- `POST /answers/{id}/accept` - Accept answer

### Notifications
- `GET /notifications/` - Get user notifications
- `GET /notifications/unread-count` - Get unread count
- `POST /notifications/{id}/read` - Mark notification as read
- `POST /notifications/mark-all-read` - Mark all as read
- `DELETE /notifications/{id}` - Delete notification

### Admin (Admin only)
- `GET /admin/users` - List all users
- `POST /admin/users/{id}/ban` - Ban user
- `POST /admin/users/{id}/unban` - Unban user
- `DELETE /admin/questions/{id}` - Delete question (admin)
- `DELETE /admin/answers/{id}` - Delete answer (admin)
- `GET /admin/stats` - Platform statistics

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  full_name: String,
  hashed_password: String,
  role: String, // "user" or "admin"
  is_active: Boolean,
  reputation: Number,
  created_at: Date,
  updated_at: Date
}
```

### Questions Collection
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  tags: [String],
  author_id: ObjectId,
  author_username: String,
  votes: Number,
  views: Number,
  answers_count: Number,
  is_answered: Boolean,
  created_at: Date,
  updated_at: Date
}
```

### Answers Collection
```javascript
{
  _id: ObjectId,
  question_id: ObjectId,
  content: String,
  author_id: ObjectId,
  author_username: String,
  votes: Number,
  is_accepted: Boolean,
  created_at: Date,
  updated_at: Date
}
```

### Notifications Collection
```javascript
{
  _id: ObjectId,
  recipient_id: ObjectId,
  type: String, // "answer", "comment", "mention", "vote"
  title: String,
  message: String,
  related_question_id: ObjectId,
  related_answer_id: ObjectId,
  sender_username: String,
  is_read: Boolean,
  created_at: Date
}
```

## User Roles & Permissions

### Guest
- View all questions and answers
- Search and filter questions
- View user profiles

### User
- All guest permissions
- Register and login
- Post questions and answers
- Vote on questions and answers
- Accept answers to own questions
- Edit own questions and answers
- Delete own questions and answers
- Receive notifications

### Admin
- All user permissions
- Ban/unban users
- Delete any question or answer
- View platform statistics
- Moderate content

## Development

### Backend Development
```bash
cd backend
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
python run.py
```

### Frontend Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.
