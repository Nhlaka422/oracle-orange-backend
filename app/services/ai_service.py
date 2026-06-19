import os
import tempfile
from typing import Dict
from google import genai

class SmartAIService:
    def __init__(self):
        self.documents = []
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if self.api_key and len(self.api_key) > 20:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("✅ Smart AI Service initialized with Google Gemini (NEW SDK)")
            except Exception as e:
                print(f"⚠️ Error initializing Gemini: {e}")
                self.client = None
        else:
            print(f"⚠️ No valid GEMINI_API_KEY found. Got: {self.api_key[:10] if self.api_key else 'None'}...")
            self.client = None

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
            if not self.client:
                return {
                    "success": True,
                    "response": self._fallback_response(question),
                    "used_context": False,
                    "documents_used": len(self.documents)
                }

            # Build context from documents
            context = ""
            if self.documents:
                context = "Document Context:\n\n"
                for doc in self.documents[-3:]:
                    context += f"--- {doc['filename']} ---\n"
                    context += doc['text'][:2000] + "\n\n"
                context = context[:6000]

            if context:
                prompt = f"""
You are Oracle Orange, an AI business analyst assistant.

{context}

User Question: {question}

Please answer based on the context above. Be thorough and professional.
"""
            else:
                prompt = f"""
You are Oracle Orange, an AI business analyst assistant.

User Question: {question}

Please provide a helpful response.
"""

            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            return {
                "success": True,
                "response": response.text,
                "used_context": bool(context),
                "documents_used": len(self.documents)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"⚠️ Gemini Error: {str(e)}"
            }

    def _fallback_response(self, question: str) -> str:
        """Fallback pattern matching response"""
        question_lower = question.lower()
        
        if "summarise" in question_lower or "summarize" in question_lower:
            if self.documents:
                doc = self.documents[-1]
                text = doc['text'][:500]
                return f"""📄 **Document Summary**

**File:** {doc['filename']}

**Content Preview:**
{text}...

**Document Stats:**
- Total characters: {len(doc['text'])}
- Word count: {len(doc['text'].split())}

What specific information would you like to know?"""
            return "No documents uploaded yet."

        return """💡 **I Can Help With:**

**Business Data Questions:**
- "Show me total revenue by month for 2024"
- "What are our top 5 selling products?"
- "Show me customer segments"

**Document Questions (after upload):**
- "Summarise the document"
- "What does the document say about X?"
- "Extract key points"

**Need something specific? Just ask!** 🚀"""

ai_service = SmartAIService()