const express = require("express");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const morgan = require("morgan");

const app = express();

app.use(bodyParser.json());
app.use(morgan("tiny"));


const Accounts = require("./routes/api/account");

const db = require("./config/key").mongoURL;
const { account } = require("./config/url");

mongoose
  .connect(db, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("MongoDB Connected...."))
  .catch((err) => console.log(err));

app.use(account, Accounts);

const port = process.env.PORT || 5050;
app.use(express.static('public'));
app.listen(port, () => console.log(`Listening in port ${port}`));
