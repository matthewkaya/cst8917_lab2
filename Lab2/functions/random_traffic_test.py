import azure.functions as func
import logging
import requests
import time
import random
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

SERVERLESS_URL = (
    "https://cst8917lab5functionapp.azurewebsites.net/api/HTTPReadDocument"
    "?id=67e2a928d3a930ef4d2d9760&StudentId=041176702"
)
CONTAINER_URL = (
    "http://cst8917lab4-username.centralus.azurecontainer.io:5000/read-document"
    "/67e2a996d3ab8a178d0d9ad4?StudentId=041176702"
)

@app.function_name(name="RandomTrafficTest")
@app.route(route="random-traffic-test", methods=["GET"])
def random_traffic_test(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("RandomTrafficTest function triggered.")

    requests_str = req.params.get('requests', '5')
    total_requests = int(requests_str)

    overall_start = time.time()
    
    # 1) Serverless requests
    serverless_times = run_random_requests(SERVERLESS_URL, total_requests)
    # 2) Container requests
    container_times = run_random_requests(CONTAINER_URL, total_requests)

    overall_end = time.time()
    total_duration = overall_end - overall_start

    avg_serverless = sum(serverless_times)/len(serverless_times) if serverless_times else 0
    avg_container = sum(container_times)/len(container_times) if container_times else 0

    log_message = (
        f"\n[RANDOM TRAFFIC TEST]\n"
        f"Total Requests: {total_requests}\n"
        f"Serverless Times: {serverless_times}\n"
        f"Container Times: {container_times}\n"
        f"Average Serverless Time: {avg_serverless:.4f}s\n"
        f"Average Container Time: {avg_container:.4f}s\n"
        f"Total Test Duration: {total_duration:.4f}s\n"
        f"--------------------------------------------\n"
    )
    write_to_log_file(log_message)

    result = {
        "total_requests": total_requests,
        "average_serverless_time": avg_serverless,
        "average_container_time": avg_container,
        "total_duration": total_duration
    }
    return func.HttpResponse(str(result), status_code=200)

def run_random_requests(url, total_requests):
    """
    Sends total_requests GET requests to the given URL. Each call is followed by
    a random delay between 0 and 5000 milliseconds.
    Returns a list of response times in seconds.
    """
    times = []
    for _ in range(total_requests):
        start = time.time()
        try:
            r = requests.get(url, timeout=30)
        except Exception as e:
            logging.warning(f"Request failed: {e}")
        end = time.time()
        times.append(end - start)

        # Delay between 0 and 5000 ms
        random_delay = random.randint(0, 5000) / 1000.0
        time.sleep(random_delay)
    return times

def write_to_log_file(message):
    # Write to /tmp directory which is writable in Azure Functions Linux
    log_filename = "/tmp/random_traffic_test.log"
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(message)

