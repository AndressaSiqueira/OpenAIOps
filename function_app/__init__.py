import azure.functions as func
from .function_app import ask_openai
from opentelemetry import trace

tracer = trace.get_tracer("http_request_handler")

def main(req: func.HttpRequest) -> func.HttpResponse:
    prompt = req.params.get('prompt')
    if not prompt:
        return func.HttpResponse("Favor fornecer o parâmetro 'prompt'", status_code=400)

    with tracer.start_as_current_span("openai_request"):
        resposta = ask_openai(prompt)

    return func.HttpResponse(resposta, status_code=200)
