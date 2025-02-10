import azure.functions as func
from functions.createDocument import main as create_document
from functions.readDocument import main as read_document

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="HTTPCreateDocument")
@app.route(route="HTTPCreateDocument", methods=["POST"])
def HTTPCreateDocument(req: func.HttpRequest) -> func.HttpResponse:
    return create_document(req)

@app.function_name(name="HTTPReadDocument")
@app.route(route="HTTPReadDocument", methods=["GET"])
def HTTPReadDocument(req: func.HttpRequest) -> func.HttpResponse:
    return read_document(req)
