from ninja import NinjaAPI

app=NinjaAPI()

@app.get('/dd')
def getpage(request,):
    return "hello Temi"