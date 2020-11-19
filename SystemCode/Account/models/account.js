const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const project_3aSchema = new Schema({
  account_number: {
    type: Number
  },
  last_4_digits_on_your_card: {
    type: Number,
  },
  fin_number: {
    type: String,
  },
  full_name: {
    type: String,
  },
  date_of_birth: {
    type: Date,
    default: Date.now,
  },
  address:{
    type: String,
  },
  phone_number:{
    type: Number,
  }
});

module.exports = account_detail = mongoose.model("account", project_3aSchema);
