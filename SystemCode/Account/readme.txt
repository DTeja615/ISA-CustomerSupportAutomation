Install node js if required

1) npm install (First Time Only)
2) npm run start to lanuch the server

** Need MongoDB to store the data


Important API Urls,

GET
http://localhost:5050/api/accounts/

GET BY account no-->1 
http://localhost:5050/api/accounts/3467589263

PUT Request
http://localhost:5050/api/accounts/3467589263

{
    "full_name": "Nick",
    "date_of_birth": "1991-07-06T08:00:00.000Z",
    "phone_number":1234567,
    "address":"address"
}

To Server HTML Files

http://localhost:5050/index.html
http://localhost:5050/details.html
http://localhost:5050/submitdetails.html