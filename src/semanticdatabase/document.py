# document.py
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class Document:
    documents: Dict[str, "Document"] = {}

    def __init__(self, name: str, root: Optional[Path]=None):
        self.name = name
        self.root_path = root or self.find_root()
        self.plugins: List["Document.Plugin"] = []
        self.db_path = self.root_path / self.name / "fragments.sqlite"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._create_table()

    def _create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS fragments (
                document TEXT NOT NULL,
                handle TEXT NOT NULL,
                language TEXT NOT NULL,
                title TEXT,
                text TEXT,
                metadata TEXT,
                PRIMARY KEY (document, handle, language)
            )
        ''')
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_all_fragments(self) -> List["Document.Fragment"]:
        try:
            cursor = self.conn.execute("SELECT document, handle, language, title, text, metadata FROM fragments")
            results = []
            for row in cursor.fetchall():
                metadata = eval(row[5]) if row[5] else None  # Simplified; consider json.loads()
                results.append(Document.Fragment(
                    document=row[0], handle=row[1], language=row[2],
                    title=row[3], text=row[4], metadata=metadata
                ))
            return results
        except sqlite3.Error as e:
            print(f'get_all_fragments({self.name}): ERROR: {e}')
            return []

    def get_fragment(self, fragment: "Document.Fragment") -> bool:
        try:
            cursor = self.conn.execute(
                "SELECT title, text, metadata FROM fragments WHERE document=? AND handle=? AND language=?",
                (fragment.document, fragment.handle, fragment.language)
            )
            row = cursor.fetchone()
            if not row:
                return False
            fragment.title = row[0]
            fragment.text = row[1]
            fragment.metadata=eval(row[2]) if row[2] else None
            return True
        except sqlite3.Error as e:
            print(f'get_fragment({self.name}, {fragment.handle}): ERROR: {e}')
            return False

    def upsert_fragment(self, fragment: "Document.Fragment"):
        try:
            self.conn.execute('''
                INSERT INTO fragments (document, handle, language, title, text, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(document, handle, language) DO UPDATE SET
                    title=excluded.title,
                    text=excluded.text,
                    metadata=excluded.metadata
            ''', (
                fragment.document,
                fragment.handle,
                fragment.language,
                fragment.title,
                fragment.text,
                repr(fragment.metadata) if fragment.metadata else None
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'upsert_fragment({self.name}, {fragment.handle}): ERROR: {e}')
            return False

    def remove_fragment(self, fragment: "Document.Fragment"):
        try:
            self.conn.execute(
                "DELETE FROM fragments WHERE document=? AND handle=? AND language=?",
                (fragment.document, fragment.handle, fragment.language)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f'upsert_delete({self.name}, {fragment.handle}): ERROR: {e}')
            return False

    def process_fragments(self, fragments: List["Document.Fragment"], **requirements):
        for key, value in requirements.items():
            for plugin in self.plugins:
                if plugin.can_handle(key, value):
                    plugin.process(fragments, key, value)
                    break
            else:
                raise ValueError(f"No plugin could handle {key}={value}")

            if not fragments:
                raise ValueError(f"No fragment found after processing {key}={value}")

    def enrich_fragment(self, fragment: "Document.Fragment", **requirements):
        fragments = [fragment]
        self.process_fragments(fragments, **requirements)
        return fragments[0]

    def search_fragments(self, **requirements) -> List["Document.Fragment"]:
        fragments: List[Document.Fragment] = []
        self.process_fragments(fragments, **requirements)
        return fragments



    class Fragment(BaseModel):
        document: str
        handle: str
        language: str
        title: Optional[str] = None
        text: Optional[str] = None
        metadata: Optional[Dict[str, Any]] = None

    class Plugin:
        def __init__(self, document: "Document"):
            self.document = document
            self._in_progress = False

        def can_handle(self, key: str, value: Any) -> bool:
            raise NotImplementedError

        def _filter(self, fragment: "Document.Fragment", key: str, value: Any):
            raise NotImplementedError

        def process(self, fragments: List["Document.Fragment"], key: str, value: Any) -> None:
            if self._in_progress:
                raise RuntimeError(f"Circular requirement detected for {key}={value}")
            try:
                self._in_progress = True
                if not fragments:
                    fragments.extend([f for f in self.document.get_all_fragments() if self._filter(f, key, value)])
                else:
                    fragments[:] = [f for f in fragments if self._filter(f, key, value)]
            finally:
                self._in_progress = False

    @classmethod
    def find_root(cls):
        for parent in Path(__file__).parent.parents:
            if (parent / '.git').is_dir() or (parent / 'data').is_dir():
                return parent / 'data'
        return Path(__file__).parent.parent / 'data'

    @classmethod
    def get(cls, name: str) -> "Document":
        if name not in cls.documents:
            cls.documents[name] = Document(name)
        return cls.documents[name]

    @classmethod
    def registry_get_fragment(cls, fragment: "Document.Fragment") -> bool:
        doc = cls.get(fragment.document)
        return doc.get_fragment(fragment)

    @classmethod
    def registry_upsert_fragment(cls, fragment: "Document.Fragment") -> bool:
        doc = cls.get(fragment.document)
        return doc.upsert_fragment(fragment)

    @classmethod
    def registry_remove_fragment(cls, fragment: "Document.Fragment") -> bool:
        doc = cls.get(fragment.document)
        return doc.remove_fragment(fragment)

    @classmethod
    def registry_wipe(cls, name: str, root: Optional[Path] = None) -> bool:
        if name in cls.documents:
            root = cls.documents[name].db_path.parent
        if root is None:
            root = cls.find_root()
        if root:
            shutil.rmtree(root)
            return True
        return False

