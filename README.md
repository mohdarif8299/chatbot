## Swagger
http://192.168.0.3:5001/docs/#/Questions/get_api_auth_student__student_id__questions

# GenAI RAG Backend Setup Guide (Local Run)

This guide explains how to set up and run your GenAI backend with:

* MongoDB Atlas
* OpenAI API
* Pinecone
* Redis (local)
* Python backend

---

## 1. Clone the repository

```bash
git clone https://github.com/mohdarif8299/chatbot.git
cd backend
cd frontend
```

---

## 2. Install Python dependencies

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

---

## 3. Prepare .env file

Create a file named `.env` inside your `backend/` folder:

```bash
cd backend
```

Paste your environment variables:

```env
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/chatbot?retryWrites=true&w=majority
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX=your-index-name
PINECONE_ENVIRONMENT=your-pinecone-region
OPENAI_API_KEY=your-openai-key
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-jwt-secret
```
---

## 4. Install and run Redis (locally)

### MacOS (with Homebrew):

```bash
brew install redis
brew services start redis
```
---

## 5. Verify Mongo Atlas Connection

Make sure your MongoDB Atlas cluster is:

* Accessible from your IP (Network Access)
* Correct username/password
* Database created: `chatbot`

You can test with Mongo Compass if needed.

---

## 6. Run the backend

First, load your environment variables:

```bash
cd backend
```

Then run your backend:

```bash
python3 run.py
```

> The backend should now be running on `http://localhost:5001`

---

## 7. Run the frontend (optional)

If you have a frontend:

```bash
cd frontend
npm install
npm run dev
```
---

## Test Cases
```bash
python3 -m unittest discover -s tests
```
