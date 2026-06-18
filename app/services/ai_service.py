import os
import tempfile
import re
from typing import Dict

class SmartAIService:
    def __init__(self):
        self.documents = []
        self.use_ollama = False  # Disable Ollama on Render
        print("✅ Smart AI Service initialized (Pattern Matching Mode)")

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

            response = self._get_ai_response(question, context)
            
            return {
                "success": True,
                "response": response,
                "used_context": bool(context),
                "documents_used": len(self.documents)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_ai_response(self, question: str, context: str = "") -> str:
        """Generate responses using pattern matching (NO AI REQUIRED)"""
        question_lower = question.lower()
        
        # Document-related questions
        if "summarise" in question_lower or "summarize" in question_lower:
            if self.documents:
                doc = self.documents[-1]
                text = doc['text'][:1000]
                return f"""📄 **Document Summary**

**File:** {doc['filename']}

**Content Preview:**
{text[:500]}...

**Document Stats:**
- Total characters: {len(doc['text'])}
- Word count: {len(doc['text'].split())}
- Line count: {len(doc['text'].splitlines())}

I've analyzed this document. What specific information would you like to know?"""
            return "No documents have been uploaded yet. Please upload a document first."

        if "document" in question_lower and self.documents:
            doc = self.documents[-1]
            return f"""📄 **Document Analysis**

**File:** {doc['filename']}
**Size:** {len(doc['text'])} characters

**Key Information:**
- The document contains {len(doc['text'].split())} words
- {len(doc['text'].splitlines())} lines of text
- Document has been processed and is ready for queries

**What would you like to know about this document?**
- "Summarise the document"
- "Extract key points"
- "Find specific information"
- "Analyze the content"
"""

        # Default response for general questions
        if not self.documents:
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

        return """💡 **I Can Help With Your Documents:**

You have uploaded documents. Ask me:
- "Summarise the document"
- "What does it say about X?"
- "Extract key points"

**Or ask about your business data:**
- "Show me total revenue by month"
- "What are our top products?"
- "Show me customer segments"
"""

ai_service = SmartAIService()