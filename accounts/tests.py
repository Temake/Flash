from django.test import TestCase
import requests

header={
    "Content-Type":"application/json",
    "Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU5NDI5Njg1LCJpYXQiOjE3NTk0MjYwODYsImp0aSI6IjFlZWI2OTAyODUzMDQwZDY4YTIzZDYwNTQ4ZjZkYTZiIiwidXNlcl9pZCI6IjEifQ.B0UFBBDlhg3TY4b-xF3f3KT7R4HPsb3sYYbMF0D-xUU"
}
# data={
#     "email":"temedia00@gmail.com",
#     "password":"123456789",
#     "confirm_password":"123456789",
#     "first_name":"yu",
#     "last_name":"Ade"
    
# }

response = requests.get("http://127.0.0.1:8082/api/conversations/",headers=header)
print(response.json())
