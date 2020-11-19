const express = require("express");
const router = express.Router();

const account_detail = require("../../models/account");

//GET
router.get("/", (req, res) => {
  account_detail.find()
    .sort({ date: -1 })
    .then((accounts) => res.json(accounts));
});


//GET BY ID
router.get("/:accNo", async (req, res) => {
  let account_number = req.params.accNo;
  const arr = await account_detail.find({ account_number: account_number });
  res.json(arr[0]);
});


//PUT
router.put("/:accNo", async (req, res) => {
  let account_number = req.params.accNo;
  let full_name= req.body.full_name;
  let date_of_birth = req.body.date_of_birth;
  let address = req.body.address;
  let phone_number = req.body.phone_number;
  const arr = await account_detail.where({ account_number: account_number }).
  update({ full_name: full_name,date_of_birth:date_of_birth,address:address,phone_number:phone_number })
  const result = await account_detail.find({ account_number: account_number });
  res.json(result[0]);
});



module.exports = router;
