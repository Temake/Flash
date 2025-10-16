from django.test import TestCase
import requests

header={
    "Content-Type":"application/json",
    "Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwNTc5NjU3LCJpYXQiOjE3NjA1NzYwNTcsImp0aSI6ImE1M2QzNmU5ZTEyNjRkZmVhMmU1MmI0NmJlNTM4ODc0IiwidXNlcl9pZCI6IjEifQ.JxCgPZJNy-84XepEyhmgR-eu6ypXXdQ3I1_kL--4JGo"
}
data={
    "email":"temedia00@gmail.com",
  
    "password":"123456789",
    # "confirm_password":"123456789",
    # "first_name":"yu",
    # "last_name":"Ade"
    # "members": [1, 2],  
    # "name": "Test Conversation",
    
}

response = requests.post("http://127.0.0.1:9000/api/login/",json=data)
print(response.json())
