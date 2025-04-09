import json
import requests

from semanticserver.models.generated import Scene, AnalysisRequest, AnalysisResult


def test_health():
    r = requests.get("http://localhost:8000/health")
    print("Health check:", r.status_code, r.json())


def test_embedding():
    payload = {"text": "C'era una volta un re molto triste."}
    r = requests.post("http://localhost:8000/embed", json=payload)
    print("Embedding result:", r.status_code, r.json())

def parse_book(filename: str):
    with open(filename) as fi:
        books = json.load(fi)
    print('uploading...')
    for bt, b in books.items():
        print(f'book: {bt}')
        for pt, p in b.items():
            print(f'    part: {pt}')
            for ct, c in p.items():
                print(f'        chapter: {ct}')
                for st, s in c.items():
                    print(f'            scene: {st}')
                    sid = f'{bt}.{pt}.{ct}.{st}'
                    text = '\n'.join(s)
                    payload = Scene(scene_id=sid, text=text, title=st)
                    r = requests.post("http://localhost:8000/scene", json=payload)
                    print("Embedding result:", r.status_code, r.json())

def test_constitution():
    from fetch_constitution import get_json

    constitution = get_json()
    print('uploading...')
    for pt, p in constitution.items():
        print(f'parte: {pt}')
        for tt, t in p.items():
            print(f'    titolo: {tt}')
            for st, s in t.items():
                print(f'        sezione: {st}')
                for at, a in s.items():
                    print(f'            articolo: {at}')
                    sid = f'{pt}.{tt}.{st}.{at}'
                    text = '\n'.join(a)
                    payload = Scene(scene_id=sid, text=text, title=at)
                    r = requests.post("http://localhost:8000/scene", json=payload.model_dump())
                    print("Embedding result:", r.status_code, r.json())



QUERIES = [
    {
        "query": "La sovranità è esercitata dal popolo nei limiti della legge.",
        "expected": ["Principi fondamentali.None.None.Art. 1"],
    },
    {
        "query": "I diritti fondamentali dell'uomo devono essere rispettati.",
        "expected": ["Principi fondamentali.None.None.Art. 2"],
    },
    {
        "query": "Le regioni possono dichiarare guerra a uno Stato straniero.",
        "expected": [],  # should have no good match
    },
    {
        "query": "L'autonomia delle regioni e degli enti locali",
        "expected": [
            "Principi fondamentali.None.None.Art. 5",
            # Add other regional autonomy articles as needed
        ],
    }
]

def test_semantic_query():
    passed = True
    min_score = 0.35
    top_k = 5
    for case in QUERIES:
        payload = AnalysisRequest(text=case['query'], top_k=5, min_score=min_score)
        r = requests.post("http://localhost:8000/analyze", json=payload.model_dump())
        print(f"\nQuery: {case['query']}")
        if r.status_code != 200:
            print(f"  ❌ Request failed with status {r.status_code}")
            passed = False
            continue

        result = AnalysisResult.model_validate_json(r.text)
        matches = result.neighbors

        print("  Matches:")
        for m in matches:
            print(f"    {m.scene_id}: score={m.similarity:.4f}")

        # Check if any expected match appears
        expected = set(case["expected"])
        returned = set(m.scene_id for m in matches)

        if expected and not (expected & returned):
            print(f"  ❌ Expected match not found. Expected one of: {expected}")
            passed = False
        elif not expected and returned:
            print(f"  ❌ Unexpected matches returned: {returned}")
            passed = False
        else:
            print(f"  ✅ Passed")

    if not passed:
        raise AssertionError("Some semantic queries did not pass.")


if __name__ == "__main__":
    test_health()
    test_embedding()
    test_constitution()
    test_semantic_query()
