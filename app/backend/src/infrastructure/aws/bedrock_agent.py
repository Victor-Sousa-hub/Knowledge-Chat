import json
import boto3
from typing import Any, Optional
from src.Domain.Interfaces.IAgentProvider import IAgentProvider
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("BedrockProvider")

class BedrockAgentProvider(IAgentProvider):
    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client("bedrock-agent-runtime", region_name=region)
        self.region = region

    def _log_trace(self, trace: dict, step: int, current_session_id: str = ""):
        """Processa e loga os eventos de trace do agente."""
        orchestration = trace.get("orchestrationTrace", {})

        # Raciocínio interno do agente (chain-of-thought)
        if "rationale" in orchestration:
            text = orchestration["rationale"].get("text", "")
            logger.debug(f"[Trace #{step}] Raciocínio: {text}")

        # Invocação de ferramenta (ex: knowledge base, action group)
        if "invocationInput" in orchestration:
            inv = orchestration["invocationInput"]
            inv_type = inv.get("invocationType", "DESCONHECIDO")
            logger.info(f"[Trace #{step}] Invocando ferramenta: {inv_type}")

            if "knowledgeBaseLookupInput" in inv:
                kb = inv["knowledgeBaseLookupInput"]
                logger.info(
                    f"[Trace #{step}] KB lookup | KB ID: {kb.get('knowledgeBaseId')} | "
                    f"Query: \"{kb.get('text')}\""
                )

            if "actionGroupInvocationInput" in inv:
                ag = inv["actionGroupInvocationInput"]
                logger.info(f"[Trace #{step}] Action Group: {ag.get('actionGroupName')} | Função: {ag.get('function')}")

        # Resultado da ferramenta invocada
        if "observation" in orchestration:
            obs = orchestration["observation"]
            obs_type = obs.get("type", "DESCONHECIDO")
            logger.info(f"[Trace #{step}] Observação: tipo={obs_type}")

            if "knowledgeBaseLookupOutput" in obs:
                results = obs["knowledgeBaseLookupOutput"].get("retrievedReferences", [])
                logger.info(f"[Trace #{step}] Documentos retornados pela KB: {len(results)}")

                for i, ref in enumerate(results):
                    s3_uri = ref.get("location", {}).get("s3Location", {}).get("uri", "URI desconhecida")
                    metadata = ref.get("metadata", {})
                    doc_session = metadata.get("session_id", "<sem session_id no metadata>")
                    content_preview = ref.get("content", {}).get("text", "")[:150].replace("\n", " ")

                    session_match = doc_session == current_session_id if current_session_id else None
                    match_label = "" if session_match is None else (" [OK]" if session_match else " [VAZAMENTO DE SESSAO!]")

                    logger.info(
                        f"[Trace #{step}] Doc {i+1}/{len(results)}{match_label} | "
                        f"S3: {s3_uri} | "
                        f"session_id no metadata: {doc_session}"
                    )
                    logger.debug(f"[Trace #{step}] Doc {i+1} conteudo: {content_preview}...")

            if "actionGroupInvocationOutput" in obs:
                output = obs["actionGroupInvocationOutput"].get("text", "")
                logger.debug(f"[Trace #{step}] Output Action Group: {output[:300]}")

            if "finalResponse" in obs:
                text = obs["finalResponse"].get("text", "")
                logger.info(f"[Trace #{step}] Resposta final gerada: {text[:200]}")

        # Erros de rastreamento
        if "failureTrace" in trace:
            reason = trace["failureTrace"].get("failureReason", "")
            logger.error(f"[Trace #{step}] FALHA: {reason}")

    def ask_agent(self,
                  agent_id: str,
                  agent_alias_id: str,
                  session_id: str,
                  prompt: str,
                  knowledge_base_id: Optional[str] = None) -> dict:
        """
        Envia o prompt para o Bedrock Agent e retorna a resposta processada.
        """
        try:
            logger.info(f"Iniciando invocação | Agente: {agent_id} | Alias: {agent_alias_id} | Sessão: {session_id}")
            logger.info(f"Pergunta: {prompt}")

            invoke_kwargs: dict[str, Any] = dict(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=prompt,
                enableTrace=True,
                endSession=False,
            )

            if knowledge_base_id:
                logger.info(f"Usando Knowledge Base: {knowledge_base_id}")
                vector_search_config: dict = {
                    "numberOfResults": 5,
                    "filter": {
                        "equals": {"key": "session_id", "value": session_id}
                    },
                }
                logger.info(f"Filtrando KB por metadata session_id: {session_id}")
                invoke_kwargs["sessionState"] = {
                    "knowledgeBaseConfigurations": [
                        {
                            "knowledgeBaseId": knowledge_base_id,
                            "retrievalConfiguration": {
                                "vectorSearchConfiguration": vector_search_config
                            }
                        }
                    ]
                }

            response = self.client.invoke_agent(**invoke_kwargs)

            full_answer = ""
            citations = []
            trace_step = 0

            for event in response.get("completion"):
                # Resposta em texto (chunks)
                if "chunk" in event:
                    chunk_text = event["chunk"]["bytes"].decode("utf-8")
                    full_answer += chunk_text
                    logger.debug(f"Chunk recebido: {chunk_text[:100]}")

                # Eventos de trace — raciocínio e passos do agente
                if "trace" in event:
                    trace_step += 1
                    self._log_trace(event["trace"].get("trace", {}), trace_step)

                # Citações da knowledge base
                if "attribution" in event.get("chunk", {}):
                    citations.append(event["chunk"]["attribution"])

            if not full_answer:
                logger.warning("Resposta vazia recebida do agente!")
            else:
                logger.info(f"Resposta final ({len(full_answer)} chars): {full_answer[:300]}")

            logger.info(f"Total de passos de raciocínio: {trace_step} | Citações: {len(citations)}")

            return {
                "answer": full_answer,
                "citations": citations
            }

        except Exception as e:
            logger.error(f"Erro ao invocar Bedrock Agent: {str(e)}")
            raise e