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

### Admin Features
- Platform basic stats
- Question and answer deletion

## Tech Stack

### Backend
- **FastAPI**
- **MongoDB**
- **JWT**

### Frontend
- **React JS**
- **Tailwind CSS**

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
Edit `.env` file with your configuration:
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
cd backend
uvicorn app.main:app --reload
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
