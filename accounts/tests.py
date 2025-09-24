from django.test import TestCase
import requests


data={
    "email":"temedia005@gmail.com"
    # "password":"123456789",
    # "confirm_password":"123456789",
    # "first_name":"Temini",
    # "last_name":"Ade",
    
}

response= requests.post("http://127.0.0.1:8081/api/forget-password/",data=data)
print(response.json())
