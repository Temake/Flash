from django.test import TestCase
import requests

header={
    "Content-Type":"application/json",
    "Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwNjEwMjM4LCJpYXQiOjE3NjA2MDY2MzgsImp0aSI6IjZlMTJiZGM1OGVkZDQ1ODlhMDZmNjlhNmMzY2IwN2I2IiwidXNlcl9pZCI6IjEifQ.ScRDgJLGn7jDcPVZsiGCUKRPilZbWkuT8E_-caf3CEY"
}
data={
    "email":"teminioluwa@gmail.com",
  
    "password":"123456789",
    # "confirm_password":"123456789",
    # "first_name":"Test ",
    # "last_name":"Testuser"
    # "members": [1, 2, 4],  
    # "name": "TrailBlazers",
    
}

response = requests.post("http://127.0.0.1:9000/api/login/",headers=header,json=data)
print(response.json())
