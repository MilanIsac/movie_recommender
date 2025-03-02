const express = require("express");
const cors = require("cors");
// const fs = require("fs");
const dotenv = require("dotenv");
require('dotenv').config({ path: '../.env' });
const connectDB = require("./config/db");
const movieRoutes = require("./routes/movieRoute");
const path = require("path");

// dotenv.config();
connectDB();

const app = express()
app.use(cors({
    origin: "*"
}))
app.use(express.json())
app.use(express.static(path.join(__dirname, "../frontend")))
app.use("/api/movies/", movieRoutes);

// const corsOptions = {
    
// };

const PORT = process.env.PORT || 5000;

app.listen(PORT, () =>{
    console.log(process.env.MONGO_URI);
    console.log(`Server is running on PORT: ${PORT}`);
});
