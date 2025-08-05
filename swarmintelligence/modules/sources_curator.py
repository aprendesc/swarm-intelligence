import os
import tiktoken
from eigenlib.LLM.sources_parser import SourcesParserClass
from eigenlib.utils.config_utils import get_config
from openai import AzureOpenAI

class SourcesCuratorClass:
    """
    Clase para curate_sources:
      - parsea con SourcesParserClass
      - cuenta tokens y estima coste
      - pide confirmación
      - chunkifica y formatea con LLM barato a Markdown
      - guarda resultado en fichero *_curated.md
    """

    def __init__(self,
                 model: str = "gpt-4.1-nano",
                 temperature: float = 0.2,
                 cost_per_1k: float = 0.0002,
                 chunk_threshold: int = 1500):
        self.global_config = get_config()
        self.model = model
        self.temperature = temperature
        self.cost_per_1k = cost_per_1k
        self.chunk_threshold = chunk_threshold

        # Cliente AzureOpenAI
        self.client = AzureOpenAI(
            azure_endpoint=self.global_config['oai_subs_1'],
            api_key=self.global_config['oai_api_key_1'],
            api_version=self.global_config['oai_api_version_1']
        )

    def _count_tokens(self, text: str) -> int:
        enc = tiktoken.encoding_for_model('gpt-4')
        return len(enc.encode(text))

    def _estimate_cost(self, n_tokens: int) -> float:
        return n_tokens / 1000 * self.cost_per_1k

    def _chunk_by_tokens(self, text: str) -> list[str]:
        """
        Trocea el texto en grupos de oraciones hasta no superar chunk_threshold tokens.
        """
        sentences = text.split(". ")
        enc = tiktoken.encoding_for_model('gpt-4')

        chunks = []
        current = []
        current_tokens = 0

        for sent in sentences:
            tok = len(enc.encode(sent))
            # si añadirlo supera el umbral, cerramos chunk
            if current and current_tokens + tok > self.chunk_threshold:
                chunks.append(" . ".join(current).strip())
                current = []
                current_tokens = 0

            current.append(sent)
            current_tokens += tok

        if current:
            chunks.append(" . ".join(current).strip())

        return chunks

    def run(self, raw_source: str) -> str:
        """
        raw_source: ruta local o URL. Devuelve la ruta del .md generado.
        """

        # 1. parsear
        SP = SourcesParserClass()
        print(f"[Curator] Parsing fuente: {raw_source}")
        parsed = SP.run(raw_source)

        # 2. tokens y coste
        total_tokens = self._count_tokens(parsed)
        estimated_cost = self._estimate_cost(total_tokens)
        print(f"[Curator] Tokens totales: {total_tokens:,}")
        print(f"[Curator] Coste estimado (model={self.model}): ${estimated_cost:.4f}")

        # 3. pedir confirmación
        confirm = input("¿Aceptas el coste y deseas continuar? [y/N]: ").lower().strip()
        if confirm != "y":
            raise RuntimeError("CurateSources cancelado por el usuario.")

        # 4. trocear
        chunks = self._chunk_by_tokens(parsed)
        print(f"[Curator] Generando {len(chunks)} chunks de máximo {self.chunk_threshold} tokens...")

        curated_chunks = []
        for i, chunk in enumerate(chunks, 1):
            print(f"[Curator] Procesando chunk {i}/{len(chunks)}...")
            system = """Eres un limpiador y formateador de texto. Recibes un fragmento y debes devolverlo en Markdown perfectamente formateado, debes replicar el texto exactamente identico pero eliminando defectos que puedan venir de errores de importación e identificando titulos subtitulos y otras estructuras, pasandolo a formato markdown. El objetivo es tener una fuente limpia y sin errores de transcripcion o parseo y en formato markdown."""
            # mandamos chunk como mensaje de usuario
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": chunk}
                ]
            )
            md = response.choices[0].message.content
            curated_chunks.append(md)

        # 5. unir
        full_curated = "\n\n".join(curated_chunks)

        # 6. guardar
        # Determinar carpeta de salida
        if os.path.isfile(raw_source):
            folder = os.path.dirname(raw_source)
            base = os.path.splitext(os.path.basename(raw_source))[0]
        else:
            # si no es fichero, guardamos en data/curated
            folder = os.path.join(self.global_config['data_path'], "curated")
            base = os.path.basename(raw_source).replace("://", "_").replace("/", "_")
        os.makedirs(folder, exist_ok=True)

        out_name = f"{base}_curated.md"
        out_path = os.path.join(folder, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_curated)

        print(f"[Curator] Fuente curada guardada en: {out_path}")
        return out_path



