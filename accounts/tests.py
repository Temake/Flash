from django.test import TestCase
import requests

header={
    "Content-Type":"application/json",
    "Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwMTgxNzIxLCJpYXQiOjE3NjAxNzgxMjEsImp0aSI6IjQ0NjRlOTZhZDVkMzQ3OTliMWM1YmEwYTY4Zjk3ZTQ3IiwidXNlcl9pZCI6IjEifQ.mNLLI5mruvB7FqW_apDKlaRcBSHJi6PrL4hxRXk4C7w"
}
data={
    # "email":"temedia00@gmail.com",
    # "password":"123456789",
    # "confirm_password":"123456789",
    # "first_name":"yu",
    # "last_name":"Ade"
    "members": [1, 2],  
    # "name": "Test Conversation",
    
}

response = requests.post("http://127.0.0.1:9000/api/conversations/",headers=header,json=data)
print(response.json())
