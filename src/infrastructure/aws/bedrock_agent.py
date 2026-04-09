import json
import boto3
from typing import List, Optional
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("BedrockProvider")

class BedrockAgentProvider:
    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client("bedrock-agent-runtime", region_name=region)
        self.region = region

    def _log_trace(self, trace: dict, step: int):
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
                logger.info(f"[Trace #{step}] Knowledge Base ID: {kb.get('knowledgeBaseId')} | Query: {kb.get('text')}")

            if "actionGroupInvocationInput" in inv:
                ag = inv["actionGroupInvocationInput"]
                logger.info(f"[Trace #{step}] Action Group: {ag.get('actionGroupName')} | Função: {ag.get('function')}")

        # Resultado da ferramenta invocada
        if "observation" in orchestration:
            obs = orchestration["observation"]
            obs_type = obs.get("type", "DESCONHECIDO")
            logger.info(f"[Trace #{step}] Resultado da observação: tipo={obs_type}")

            if "knowledgeBaseLookupOutput" in obs:
                results = obs["knowledgeBaseLookupOutput"].get("retrievedReferences", [])
                logger.info(f"[Trace #{step}] Documentos recuperados da KB: {len(results)}")
                for i, ref in enumerate(results):
                    content = ref.get("content", {}).get("text", "")[:200]
                    source = ref.get("location", {})
                    logger.debug(f"[Trace #{step}] Doc {i+1}: {content}... | Fonte: {source}")

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

            invoke_kwargs = dict(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=prompt,
                enableTrace=True,
                endSession=False,
            )

            if knowledge_base_id:
                logger.info(f"Usando Knowledge Base: {knowledge_base_id}")
                invoke_kwargs["sessionState"] = {
                    "knowledgeBaseConfigurations": [
                        {
                            "knowledgeBaseId": knowledge_base_id,
                            "retrievalConfiguration": {
                                "vectorSearchConfiguration": {
                                    "numberOfResults": 5
                                }
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