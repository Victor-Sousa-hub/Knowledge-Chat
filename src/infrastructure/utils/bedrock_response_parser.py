from dataclasses import dataclass, field


@dataclass
class SourceReference:
    file_name: str
    uri: str
    pages: list[int] = field(default_factory=list)


@dataclass
class ParsedAgentResponse:
    answer: str
    sources: list[SourceReference]

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "sources": [
                {
                    "file": src.file_name,
                    "uri": src.uri,
                    "pages": sorted(src.pages),
                }
                for src in self.sources
            ],
        }


class BedrockResponseParser:
    """Parses the raw Bedrock Agent response into answer text and source references."""

    def parse(self, raw: dict) -> ParsedAgentResponse:
        answer = raw.get("answer", "")
        sources = self._extract_sources(raw.get("citations", []))
        return ParsedAgentResponse(answer=answer, sources=sources)

    def _extract_sources(self, citation_groups: list) -> list[SourceReference]:
        # Deduplicate sources by URI, accumulating unique pages
        sources_by_uri: dict[str, SourceReference] = {}

        for group in citation_groups:
            for citation in group.get("citations", []):
                for ref in citation.get("retrievedReferences", []):
                    uri = ref.get("location", {}).get("s3Location", {}).get("uri", "")
                    if not uri:
                        continue

                    page = ref.get("metadata", {}).get(
                        "x-amz-bedrock-kb-document-page-number"
                    )
                    file_name = uri.split("/")[-1]

                    if uri not in sources_by_uri:
                        sources_by_uri[uri] = SourceReference(
                            file_name=file_name, uri=uri
                        )

                    if page is not None and page not in sources_by_uri[uri].pages:
                        sources_by_uri[uri].pages.append(page)

        return list(sources_by_uri.values())
