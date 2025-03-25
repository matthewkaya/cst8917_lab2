import azure.functions as func
import logging
import requests
import time
import concurrent.futures
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Final URLs based on your latest POST/GET tests
SERVERLESS_URL = (
    "https://cst8917lab5functionapp.azurewebsites.net/api/HTTPReadDocument"
    "?id=67e2a928d3a930ef4d2d9760&StudentId=041176702"
)
CONTAINER_URL = (
    "http://cst8917lab4-username.centralus.azurecontainer.io:5000/read-document"
    "/67e2a996d3ab8a178d0d9ad4?StudentId=041176702"
)

@app.function_name(name="TrafficSurgeTest")
@app.route(route="traffic-surge-test", methods=["GET"])
def traffic_surge_test(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("TrafficSurgeTest function triggered.")
    
    # Number of parallel requests (default = 5 if not specified)
    parallel_str = req.params.get('parallel', '5')
    parallel_count = int(parallel_str)
    
    overall_start = time.time()
    
    # 1) Serverless parallel requests
    serverless_times = run_parallel_requests(SERVERLESS_URL, parallel_count)
    # 2) Container parallel requests
    container_times = run_parallel_requests(CONTAINER_URL, parallel_count)
    
    overall_end = time.time()
    total_duration = overall_end - overall_start
    
    avg_serverless = sum(serverless_times) / len(serverless_times) if serverless_times else 0
    avg_container = sum(container_times) / len(container_times) if container_times else 0
    
    log_message = (
        f"\n[TRAFFIC SURGE TEST]\n"
        f"Parallel Requests: {parallel_count}\n"
        f"Serverless Times: {serverless_times}\n"
        f"Container Times: {container_times}\n"
        f"Average Serverless Time: {avg_serverless:.4f}s\n"
        f"Average Container Time: {avg_container:.4f}s\n"
        f"Total Test Duration: {total_duration:.4f}s\n"
        f"--------------------------------------------\n"
    )
    write_to_log_file(log_message)
    
    result = {
        "parallel_requests": parallel_count,
        "average_serverless_time": avg_serverless,
        "average_container_time": avg_container,
        "total_duration": total_duration
    }
    return func.HttpResponse(str(result), status_code=200)

def run_parallel_requests(url, parallel_count):
    """
    Sends parallel_count GET requests to the provided URL concurrently.
    Returns a list of response times (seconds).
    """
    times = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_count) as executor:
        futures = [executor.submit(measure_request_time, url) for _ in range(parallel_count)]
        for f in concurrent.futures.as_completed(futures):
            times.append(f.result())
    return times

def measure_request_time(url):
    """
    Sends a GET request to the given URL and measures its response time in seconds.
    """
    start = time.time()
    try:
        r = requests.get(url, timeout=30)
        # optionally check r.status_code, r.text
    except Exception as e:
        logging.warning(f"Request failed: {e}")
    end = time.time()
    return end - start

def write_to_log_file(message):
    # Write to /tmp directory which is writable in Azure Functions Linux
    log_filename = "/tmp/traffic_surge_test.log"
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(message)

