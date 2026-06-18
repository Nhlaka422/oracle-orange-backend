import os
import tempfile
import requests
import json
from typing import Dict

class SmartAIService:
    def __init__(self):
        self.documents = []
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.2:3b"
        self._check_ollama()
        print(f"✅ Smart AI Service initialized with Ollama (Model: {self.model})")

    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434", timeout=2)
            if response.status_code == 200:
                print("✅ Ollama is running!")
            else:
                print("⚠️ Ollama is running but returned unexpected status")
        except:
            print("⚠️ Ollama is NOT running!")
            print("Please start Ollama first:")
            print("  ollama serve")

    def process_document(self, file_content: bytes, filename: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                tmp_file.write(file_content)
                tmp_path = tmp_file.name

            text = ""
            
            if filename.endswith('.pdf'):
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(tmp_path)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                except:
                    text = f"PDF file: {filename}"
            
            elif filename.endswith('.txt'):
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            elif filename.endswith('.docx'):
                try:
                    import docx
                    doc = docx.Document(tmp_path)
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                except:
                    text = f"DOCX file: {filename}"
            
            elif filename.endswith('.csv'):
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            else:
                text = f"File: {filename}"
            
            os.unlink(tmp_path)
            return text[:5000]

        except Exception as e:
            return f"Error: {str(e)}"

    def add_document_to_knowledge_base(self, file_content: bytes, filename: str, metadata: Dict = None) -> Dict:
        text = self.process_document(file_content, filename)
        
        self.documents.append({
            "filename": filename,
            "text": text,
            "metadata": metadata or {}
        })

        return {
            "success": True,
            "message": f"Added document: {filename}",
            "total_documents": len(self.documents)
        }

    def query_with_context(self, question: str) -> Dict:
        try:
            context = ""
            if self.documents:
                context = "Document Context:\n\n"
                for doc in self.documents[-3:]:
                    context += f"--- {doc['filename']} ---\n"
                    context += doc['text'][:2000] + "\n\n"
                context = context[:6000]

            if context:
                prompt = f"""You are Oracle Orange, a business analyst AI assistant.

{context}

User Question: {question}

Please answer based on the context above. If the context doesn't contain the exact answer, use your general knowledge but be honest about it. Be thorough and professional in your response."""
            else:
                prompt = f"""You are Oracle Orange, a business analyst AI assistant.

User Question: {question}

Please provide a helpful, thorough response. If you don't know something, be honest about it."""

            response = self._get_ai_response(prompt)
            
            return {
                "success": True,
                "response": response,
                "used_context": bool(context),
                "documents_used": len(self.documents)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_ai_response(self, prompt: str) -> str:
        """Get response from Ollama"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response from AI")
            else:
                return f"⚠️ **Ollama Error: {response.status_code}**\n\n{response.text[:200]}"

        except requests.exceptions.Timeout:
            return "⚠️ **Timeout:** The AI is taking too long. Try a simpler question."
        except requests.exceptions.ConnectionError:
            return """⚠️ **Connection Error:** Can't reach Ollama.

Make sure Ollama is running:
1. Open the Ollama app
2. Or run: `ollama serve`
3. Then try again!"""
        except Exception as e:
            return f"⚠️ **AI Error:** {str(e)}"

ai_service = SmartAIService()