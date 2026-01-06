const express = require('express');
const { google } = require('googleapis');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: '../.env' });

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;

app.get('/api/leads', async (req, res) => {
    // Check if we should use local mode
    const isLocal = !(process.env.SPREADSHEET_ID && process.env.GOOGLE_CREDENTIALS_PATH);

    if (isLocal) {
        try {
            const localPath = path.join(__dirname, '../local_leads.json');
            if (fs.existsSync(localPath)) {
                const data = fs.readFileSync(localPath, 'utf8');
                return res.json(json_decode(data));
            }
            return res.json([]);
        } catch (error) {
            return res.status(500).json({ error: 'Local data read error' });
        }
    }

    try {
        const credPath = path.isAbsolute(process.env.GOOGLE_CREDENTIALS_PATH)
            ? process.env.GOOGLE_CREDENTIALS_PATH
            : path.join(__dirname, '..', process.env.GOOGLE_CREDENTIALS_PATH);

        const auth = new google.auth.GoogleAuth({
            keyFile: credPath,
            scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
        });
        const sheets = google.sheets({ version: 'v4', auth });
        const response = await sheets.spreadsheets.values.get({
            spreadsheetId: process.env.SPREADSHEET_ID,
            range: 'Sheet1!A2:Z',
        });

        const rows = response.data.values || [];
        const leads = rows.map((row, index) => ({
            row_index: index + 2,
            lead_id: row[0], first_name: row[1], last_name: row[2],
            email: row[3], linkedin_url: row[4], company_name: row[5],
            company_website: row[6], role: row[7], intent_score: row[8],
            status: row[9], status_note: row[10], last_processed_at: row[11],
            next_action_at: row[12], company_summary: row[13], personal_hook: row[14],
            angle: row[15], cta: row[16], email_subject: row[17],
            email_body: row[18], email_sent_at: row[19], email_message_id: row[20],
            linkedin_post: row[21]
        }));
        res.json(leads);
    } catch (error) {
        console.error('API Error:', error.message);
        res.status(500).json({ error: 'Google Sheets fetch failed' });
    }
});

function json_decode(text) { try { return JSON.parse(text); } catch { return []; } }

app.listen(PORT, () => {
    console.log(`API running on http://localhost:${PORT} (${!(process.env.SPREADSHEET_ID) ? 'MOCK MODE' : 'REMOTE MODE'})`);
});
