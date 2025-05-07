from openai import AzureOpenAI
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# ========== CONFIGURAÇÃO ==========
configure_azure_monitor(
    connection_string="InstrumentationKey=6e089b0c-78b0-41d7-b74e-af7c8e0b8f36;IngestionEndpoint=https://eastus2-3.in.applicationinsights.azure.com/"
)

AZURE_OPENAI_ENDPOINT = "https://dessa.openai.azure.com"
AZURE_OPENAI_API_KEY = "RMiQPBLVTZkxPwYJrySUbGCxx9EoxEfUrMIz7AC7MNN4VBvxuByEJQQJ99BEACHYHv6XJ3w3AAABACOGwqRI"
AZURE_OPENAI_DEPLOYMENT = "modeldessa"

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2025-01-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

tracer = trace.get_tracer(__name__)

def ask_openai(prompt: str) -> str:
    with tracer.start_as_current_span("call_openai") as span:
        try:
            span.set_attribute("user.prompt", prompt)
            response = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content
            span.set_status(Status(StatusCode.OK))
            return answer
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            return "Erro ao chamar o modelo."
