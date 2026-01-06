# Start all components of the Lead Automation System

Write-Host "🚀 Starting AI Lead Automation System..." -ForegroundColor Cyan

# 1. Start Dashboard API
Write-Host "📡 Starting API Bridge on http://localhost:3001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd dashboard-api; node server.js"

# 2. Start Dashboard UI
Write-Host "💻 Starting Frontend Canvas on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd dashboard-ui; npm run dev"

# 3. Start Backend Automation Loop
Write-Host "🤖 Starting Backend Research Loop..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py"

Write-Host "✅ All systems initiated! Check the individual windows for logs." -ForegroundColor Green
Write-Host "⚠️  Reminder: Ensure your .env file is configured with API keys before starting." -ForegroundColor Red
