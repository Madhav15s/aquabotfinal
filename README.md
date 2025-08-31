# 🚢 IME Hub Maritime AI Assistant

A professional, full-stack maritime AI platform with multi-agent capabilities for voyage planning, cargo matching, market insights, port intelligence, and PDA management.

## ✨ Features

- **🤖 Multi-Agent System**: 6 specialized maritime AI agents
- **📄 Document Analysis**: Upload and analyze voyage documents
- **🌤️ Real-time Weather**: Live weather data integration
- **🚢 Vessel Tracking**: AIS data management system
- **🧠 AI Reasoning**: Advanced LLM integration
- **💻 Modern UI**: React frontend with Apple liquid glass design

## 🏗️ Architecture

```
ime-hub-maritime-ai/
├── backend/                 # Python FastAPI backend
│   ├── agents/             # AI agent modules
│   ├── apis/               # External API integrations
│   ├── data/               # Static datasets
│   └── main.py             # Main application entry
├── frontend/                # React frontend
│   └── src/components/     # UI components
└── docs/                    # Sample documents for testing
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Windows Users
```bash
# Use the provided batch file
start.bat

# Or PowerShell
.\start.ps1
```

## 🤖 AI Agents

1. **Captain Router** - Intelligent routing and general assistance
2. **Voyage Planner** - Route optimization and weather routing
3. **Cargo Matcher** - Vessel-cargo pairing and profitability
4. **Market Insights** - Freight rates and market analysis
5. **Port Intelligence** - Port data and bunker availability
6. **PDA Management** - Port disbursement and cost tracking

## 📄 Document Support

Upload and analyze:
- Charter Party agreements
- Voyage planning documents
- Port disbursement accounts
- Market analysis reports
- Cargo specifications

## 🔧 API Integrations

- **Weather API**: OpenWeatherMap integration
- **AIS Data**: CSV-based vessel tracking system
- **LLM API**: Google Gemini integration

## 🌐 Access

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 📝 Sample Documents

Test the system with sample documents in the `docs/` folder:
- `sample_charter_party.md` - Charter party agreement
- `voyage_planning_document.md` - Voyage planning details
- `port_disbursement_account.md` - PDA breakdown

## 🎯 Use Cases

- **Voyage Planning**: Route optimization with weather considerations
- **Cargo Matching**: Find optimal vessel-cargo combinations
- **Cost Analysis**: PDA estimates and voyage cost calculations
- **Market Intelligence**: Freight rates and market trends
- **Document Analysis**: AI-powered document summarization

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, Pandas
- **Frontend**: React, Framer Motion, CSS3
- **AI**: Custom NLP, LLM integration
- **Data**: JSON datasets, CSV management
- **APIs**: Weather, AIS, LLM services

## 📞 Support

For technical support or questions, refer to the system documentation or contact the development team.

---

**IME Hub Maritime AI Assistant** - Professional Maritime Intelligence Platform 