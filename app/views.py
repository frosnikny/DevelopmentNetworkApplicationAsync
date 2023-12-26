from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests

from concurrent import futures

CALLBACK_URL = "http://localhost:8080/api/requests/"

executor = futures.ThreadPoolExecutor(max_workers=1)
TOKEN = 'a157b23c'


def get_random_status(customer_request_id):
    time.sleep(5)
    return {
        "customer_request_id": customer_request_id,
        "status": bool(random.randint(0, 4)),
    }


def status_callback(task):
    try:
        result = task.result()
        print(result)
    except futures._base.CancelledError:
        return

    url = str(CALLBACK_URL+str(result["customer_request_id"])+'/payment/')
    requests.put(url, data={"payment_status": result['status'], "token": TOKEN}, timeout=3)


@api_view(['POST'])
def set_status(request):
    if "customer_request_id" in request.data.keys():
        customer_request_id = request.data["customer_request_id"]

        task = executor.submit(get_random_status, customer_request_id)
        task.add_done_callback(status_callback)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
