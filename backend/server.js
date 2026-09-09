require("dotenv").config();
const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;

const APP_VERSION = process.env.APP_VERSION || "dev";

app.get("/", (req, res) => {
    res.json({
        application: "Versioned Release Platform",
        version: APP_VERSION,
        status: "running"
    });
});

app.get("/api/health", (req, res) => {
    res.json({
        status: "healthy",
        version: APP_VERSION
    });
});

app.get("/api/version", (req, res) => {
    res.json({
        version: APP_VERSION
    });
});

app.listen(PORT, () => {
    console.log(`Backend running on port ${PORT}`);
    console.log(`Application version: ${APP_VERSION}`);
});