import os
import tempfile
from typing import Dict
from google import genai

class SmartAIService:
    def __init__(self):
        self.documents = []
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_names = [
            'gemini-1.5-flash',      # Most likely to work
            'gemini-1.5-pro',        # More capable
            'gemini-pro',            # Older version
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-pro',
        ]
        self.working_model = None
        
        if self.api_key and len(self.api_key) > 20:
            try:
                self.client = genai.Client(api_key=self.api_key)
                # Try to find a working model
                self._find_working_model()
                if self.working_model:
                    print(f"✅ Smart AI Service initialized with Google Gemini ({self.working_model})")
                else:
                    print(f"⚠️ No working Gemini model found. Using fallback.")
                    self.client = None
            except Exception as e:
                print(f"⚠️ Error initializing Gemini: {e}")
                self.client = None
        else:
            print(f"⚠️ No valid GEMINI_API_KEY found. Got: {self.api_key[:10] if self.api_key else 'None'}...")
            self.client = None

    def _find_working_model(self):
        """Find a working model by testing each one"""
        for model_name in self.model_names:
            try:
                test_response = self.client.models.generate_content(
                    model=model_name,
                    contents="Hello, are you working?"
                )
                if test_response and test_response.text:
                    self.working_model = model_name
                    print(f"✅ Found working model: {model_name}")
                    return True
            except Exception as e:
                print(f"❌ Model {model_name} failed: {str(e)[:50]}...")
                continue
        return False

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
            # If no client or working model, use fallback
            if not self.client or not self.working_model:
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
                model=self.working_model,
                contents=prompt
            )
            
            return {
                "success": True,
                "response": response.text,
                "used_context": bool(context),
                "documents_used": len(self.documents)
            }

        except Exception as e:
            # If Gemini fails, use fallback
            return {
                "success": True,
                "response": self._fallback_response(question),
                "used_context": False,
                "documents_used": len(self.documents)
            }

    def _fallback_response(self, question: str) -> str:
        """Fallback pattern matching response"""
        question_lower = question.lower()
        
        # Document summarization
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
            return "No documents uploaded yet. Please upload a document first."

        # Document analysis
        if "document" in question_lower and self.documents:
            doc = self.documents[-1]
            return f"""📄 **Document Analysis**

**File:** {doc['filename']}
**Size:** {len(doc['text'])} characters

**Key Information:**
- {len(doc['text'].split())} words
- {len(doc['text'].splitlines())} lines

What would you like to know about this document?
- "Summarise the document"
- "Extract key points"
- "Find specific information"
"""

        # Generic response
        return """💡 **I Can Help With:**

**Business Data Questions:**
- "Show me total revenue by month for 2024"
- "What are our top 5 selling products?"
- "Show me customer segments"
- "What's the average order value?"

**Document Questions (after upload):**
- "Summarise the document"
- "What does the document say about X?"
- "Extract key points"

**Need something specific? Just ask!** 🚀"""

ai_service = SmartAIService()