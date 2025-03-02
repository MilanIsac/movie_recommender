const mongoose = require("mongoose");
require("dotenv").config();
require('dotenv').config({ path: '../.env' });

const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI, {
            // useNewUrlParser: true,
            // useUnifiedTopology: true,
        });
        console.log("Mongo connected");
    } catch (error) {
        console.error("Mongo connection error: ", error);
        process.exit(1);
    }
};

module.exports = connectDB;