from typing import Any

from document import Document

class StupidNameMatcher(Document.Plugin):

    def can_handle(self, key: str, value: Any) -> bool:
        return key == "character"

    def _filter(self, fragment: "Document.Fragment", key: str, value: Any):
        return fragment.text and value.lower() in fragment.text.lower()


doc = Document.get("test-doc")
doc.upsert_fragment(Document.Fragment(document="test-doc", handle="scene1", language="it", text="Mario incontra Lucia nel giardino."))
doc.upsert_fragment(Document.Fragment(document="test-doc", handle="scene2", language="it", text="Lucia discute con Giovanni."))
doc.upsert_fragment(Document.Fragment(document="test-doc", handle="scene3", language="it", text="Mario e Lucia si riconciliano."))
doc.plugins.append(StupidNameMatcher(doc))

print("--- Search for fragments mentioning Lucia ---")
results = []
try:
    results = doc.search_fragments(character="Mario")
except Exception as e:
    print("Error:", e)

for f in results:
    print(f"{f.handle}: {f.text}")