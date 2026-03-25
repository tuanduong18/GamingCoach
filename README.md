# GamingCoach 🎮

GamingCoach is an intelligent League of Legends coaching application that leverages the power of Google Gemini AI to analyze your recent matches and provide actionable, data-driven advice to help you climb the ladder.

<img width="1803" height="937" alt="image" src="https://github.com/user-attachments/assets/ba9d74d1-5843-4acd-9a95-91a7421ae222" />
<img width="1701" height="928" alt="image" src="https://github.com/user-attachments/assets/b06b2e41-ef1f-4038-9142-54552247e8ff" />
<img width="1454" height="943" alt="image" src="https://github.com/user-attachments/assets/88c9cd12-3171-46cc-b823-bfc1883baa02" />




---

## 🚀 Features

- **Match Analysis**: Fetches your latest match history using the Riot Games API.
- **AI-Powered Coaching**: Uses Google Gemini to analyze performance metrics and provide granular feedback.
- **Data Visualization**: Interactive charts showing gold differences, damage distribution, and more via Recharts.
- **Multi-Region Support**: Supports NA, EUW, KR, and other major Riot regions.
- **Dockerized Setup**: Seamless deployment with Docker Compose.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **API Integration**: [RiotWatcher](https://github.com/pseudonym117/RiotWatcher)
- **AI Service**: [Google Generative AI (Gemini)](https://ai.google.dev/)
- **Validation**: [Pydantic](https://docs.pydantic.dev/)

### Frontend
- **Framework**: [React](https://reactjs.org/) (TypeScript)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **UI Components**: [Bootstrap](https://getbootstrap.com/)
- **Charts**: [Recharts](https://recharts.org/)
- **Markdown Rendering**: [React-Markdown](https://github.com/remarkjs/react-markdown)

---

## ⚙️ Setup & Installation

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop/) & Docker Compose
- [Riot Games API Key](https://developer.riotgames.com/)
- [Google Gemini API Key](https://aistudio.google.com/app/apikey)

### 1. Clone the repository
```bash
git clone https://github.com/tuanduong18/GamingCoach.git
cd GamingCoach
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
RIOT_API_KEY=your_riot_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run with Docker (Recommended)
```bash
docker-compose up --build
```
The application will be available at:
- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`

---

## 🛠️ Manual Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📂 Project Structure

```text
GamingCoach/
├── backend/            # FastAPI Backend
│   ├── ai_service.py   # Gemini AI Integration
│   ├── riot_api.py     # Riot API logic
│   └── main.py         # Entry point
├── frontend/           # React Frontend (Vite)
│   ├── src/            # Components & Logic
│   └── public/         # Static assets
├── docker-compose.yml  # Docker orchestration
└── .env                # Secrets (Ignored by Git)
```

---

## 📜 License
This project is for educational purposes. League of Legends and Riot Games are trademarks of Riot Games, Inc.
