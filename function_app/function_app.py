from openai import AzureOpenAI
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.sdk.resources import Resource  # Importação necessária

# ========== CONFIGURAÇÃO ==========

# Configura o Azure Monitor para enviar dados de rastreamento para o Application Insights
configure_azure_monitor(
    connection_string="InstrumentationKey=3c509b15-fe24-4d39-b1ef-9edd3c3518fb;IngestionEndpoint=https://eastus2-3.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus2.livediagnostics.monitor.azure.com/;ApplicationId=50e58161-a4c6-47ec-8a10-503bc2a3cce6",
    resource=Resource.create({
        "service.name": "OpenAI_FunctionApp",  # Nome amigável para sua função
        "service.instance.id": "instance-1"   # Identificador único da instância
    }))
# Configuração da API do Azure OpenAI
AZURE_OPENAI_ENDPOINT = "https://dessa.openai.azure.com"
AZURE_OPENAI_API_KEY = "RMiQPBLVTZkxPwYJrySUbGCxx9EoxEfUrMIz7AC7MNN4VBvxuByEJQQJ99BEACHYHv6XJ3w3AAABACOGwqRI"
AZURE_OPENAI_DEPLOYMENT = "modeldessa"

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2025-01-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Obtém o tracer para rastrear a chamada
tracer = trace.get_tracer(__name__)

def ask_openai(prompt: str) -> str:
    # Cria um span para rastrear a dependência como uma chamada externa (HTTP)
    with tracer.start_as_current_span("call_openai", kind=SpanKind.CLIENT) as span:
        try:
            # Define atributos HTTP para a dependência
            span.set_attribute("http.url", f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions")
            span.set_attribute("http.method", "POST")
            span.set_attribute("user.prompt", prompt)
            
            # Realiza a chamada à API do OpenAI
            response = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[{"role": "user", "content": prompt}]
            )

            # Resposta gerada pelo modelo
            answer = response.choices[0].message.content

            # Marca o span como bem-sucedido
            span.set_status(Status(StatusCode.OK))
            print(f"Span status: {span.status.status_code}")  # Para depuração local
            return answer
        except Exception as e:
            # Caso ocorra algum erro, marca o span como erro e registra a exceção
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            print(f"Erro no span: {span.status.status_code}, Exceção: {str(e)}")  # Para depuração local
            return "Erro ao chamar o modelo."
