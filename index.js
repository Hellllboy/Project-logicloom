const express = require("express");
const bodyParser = require("body-parser");
const mongoose = require("mongoose");
const path = require("path");
const openai = require("openai");

const app = express();

app.use(bodyParser.json());
app.use(express.static('public'));
app.use(bodyParser.urlencoded({
    extended: true
}));

mongoose.connect('mongodb://localhost:27017/formpage');
const db = mongoose.connection;
db.on('error', () => console.log("Error in connecting the database"));
db.once('open', () => console.log("Connected to database"));

// Set your OpenAI API key
const OPENAI_API_KEY = "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";

app.post("/submit_feedback", async (req, res) => {
    const name = req.body.name;
    const email = req.body.email;
    const country = req.body.country;
    const feedback = req.body.feedback;
    const rating = req.body.rating;
    const recommend = req.body.recommend === 'yes' ? 1 : 0;

    // Summarize the feedback using OpenAI API
    const summary = await summarizeFeedback(feedback);

    const data = {
        "name": name,
        "email": email,
        "country": country,
        "feedback": feedback,
        "rating": rating,
        "recommend": recommend,
        "summary": summary
    };

    db.collection('users').insertOne(data, (err, collection) => {
        if (err) {
            throw err;
        }
        console.log("Feedback Submitted Successfully");
    });

    // Assuming you have a signup_successful.html file in the public folder
    const signupSuccessfulPath = path.join(__dirname, 'public', 'signup_successful.html');
    return res.sendFile(signupSuccessfulPath);
});

app.get("/", (req, res) => {
    res.set({
        "Allow-access-Allow-origin": '*'
    });
    const indexPath = path.join(__dirname, 'public', 'index.html');
    return res.sendFile(indexPath);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});

async function summarizeFeedback(text) {
    try {
        const response = await openai.completions.create({
            engine: "text-davinci-003",
            prompt: text,
            max_tokens: 50
        });

        return response.choices[0].text.trim();
    } catch (error) {
        console.error("Error in OpenAI API request:", error);
        return "Summary not available";
    }
}
