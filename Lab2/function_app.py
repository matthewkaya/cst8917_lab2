import azure.functions as func
from functions.createDocument import main as create_document
from functions.readDocument import main as read_document

from functions.traffic_surge_test import traffic_surge_test
from functions.consistent_traffic_test import consistent_traffic_test
from functions.random_traffic_test import random_traffic_test

# Create a single FunctionApp object
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# -----------------------------
# Lab 2 Functions
# -----------------------------

@app.function_name(name="HTTPCreateDocument")
@app.route(route="create-document", methods=["POST"])
def HTTPCreateDocument(req: func.HttpRequest) -> func.HttpResponse:
    return create_document(req)


@app.function_name(name="HTTPReadDocument")
@app.route(route="read-document", methods=["GET"])
def HTTPReadDocument(req: func.HttpRequest) -> func.HttpResponse:
    return read_document(req)

# -----------------------------
# Lab 5 Functions
# -----------------------------

@app.function_name(name="TrafficSurgeTest")
@app.route(route="traffic-surge-test", methods=["GET"])
def traffic_surge_test_handler(req: func.HttpRequest) -> func.HttpResponse:
   return traffic_surge_test(req)

@app.function_name(name="ConsistentTrafficTest")
@app.route(route="consistent-traffic-test", methods=["GET"])
def consistent_traffic_test_handler(req: func.HttpRequest) -> func.HttpResponse:
    return consistent_traffic_test(req)

@app.function_name(name="RandomTrafficTest")
@app.route(route="random-traffic-test", methods=["GET"])
def random_traffic_test_handler(req: func.HttpRequest) -> func.HttpResponse:
    return random_traffic_test(req)