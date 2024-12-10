import azure.functions as func
from azure.data.tables import TableServiceClient
from dotenv import load_dotenv
import os
import logging
import uuid
import json

load_dotenv()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

TABLE_NAME = "ToDoTable"

def get_table_client():
    connection_string = os.environ["AzureWebJobsStorage"]
    service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = service_client.get_table_client(TABLE_NAME)
    return table_client

@app.route(route="todos", methods=["POST"])
def create_todo(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        task_id = str(uuid.uuid4())
        task = {
            "PartitionKey": "ToDo",
            "RowKey": task_id,
            "Task": body.get("task"),
            "Status": "Pending"
        }
        table_client = get_table_client()
        table_client.create_entity(task)
        return func.HttpResponse(f"Task created with ID: {task_id}", status_code=201)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)

@app.route(route="todos", methods=["GET"])  
def get_todos1(req: func.HttpRequest) -> func.HttpResponse:
    try:
        table_client = get_table_client()
        entities = table_client.query_entities(query_filter="PartitionKey eq 'ToDo'")
        tasks = [entity for entity in entities]
        return func.HttpResponse(body=json.dumps(tasks), status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)

@app.route(route="todos/{task_id}", methods=["GET"])
def get_todos2(req: func.HttpRequest) -> func.HttpResponse:
    try:
        task_id = req.route_params.get("task_id")
        table_client = get_table_client()
        entity = table_client.get_entity(partition_key="ToDo", row_key=task_id)
        return func.HttpResponse(body=json.dumps(entity), status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=404)
    
@app.route(route="todos/{task_id}", methods=["PUT"])
def update_todo1(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        task_id = req.route_params.get("task_id")
        table_client = get_table_client()
        entity = table_client.get_entity(partition_key="ToDo", row_key=task_id)
        entity["Status"] = body.get("status")
        table_client.update_entity(entity)
        return func.HttpResponse(f"Task with ID: {task_id} updated", status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=404)
    
@app.route(route="todos/{task_id}", methods=["DELETE"])
def delete_todo1(req: func.HttpRequest) -> func.HttpResponse:
    try:
        table_client = get_table_client()
        task_id = req.route_params.get("task_id")
        table_client.delete_entity(partition_key="ToDo", row_key=task_id)
        return func.HttpResponse(f"Task with ID: {task_id} deleted", status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=404)


