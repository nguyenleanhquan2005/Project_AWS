import boto3
import json
import uuid
import math
import pypdf
import re

class BedrockRAG:
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.chunk_size = 800
        self.chunk_overlap = 100
    
    def get_titan_embedding(self, text):
        """Lấy embedding từ Amazon Titan (FREE)"""
        try:
            # Clean text để tránh lỗi
            clean_text = text.replace('\x00', '').strip()
            if not clean_text:
                return None
                
            body = json.dumps({
                "inputText": clean_text
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId='amazon.titan-embed-text-v1',
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
            
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    def invoke_claude(self, prompt, max_tokens=1000):
        """Gọi Claude cho generation"""
        try:
            body = json.dumps({
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-instant-v1',
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['completion']
            
        except Exception as e:
            print(f"Claude error: {e}")
            return None
    
    def invoke_titan(self, prompt, max_tokens=1000):
        """Gọi Amazon Titan cho generation (FREE)"""
        try:
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": 0.7,
                    "topP": 0.9,
                }
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId='amazon.titan-text-lite-v1',
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['results'][0]['outputText']
            
        except Exception as e:
            print(f"Titan error: {e}")
            return None
    
    def load_and_split_document(self, file_path):
        """Load và chia nhỏ document"""
        print(f"📖 Loading document: {file_path}")
        
        try:
            if file_path.lower().endswith('.pdf'):
                text = self._extract_pdf_text(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            chunks = self._split_text(text)
            print(f"📄 Split into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            print(f"❌ Document loading error: {e}")
            return []
    
    def _extract_pdf_text(self, file_path):
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _split_text(self, text):
        """Split text into chunks"""
        # Simple text splitting
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append({"page_content": current_chunk.strip()})
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append({"page_content": current_chunk.strip()})
            
        return chunks
    
    def cosine_similarity(self, a, b):
        """Tính cosine similarity giữa 2 vectors"""
        if not a or not b or len(a) != len(b):
            return -1
        
        try:
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            
            if norm_a == 0 or norm_b == 0:
                return -1
                
            return dot / (norm_a * norm_b)
        except Exception as e:
            print(f"Cosine similarity error: {e}")
            return -1
    
    def create_vector_store(self, chunks):
        """Tạo vector store với Titan embeddings (không dùng FAISS)"""
        print("🔄 Creating vector store với Titan embeddings...")
        
        texts = [chunk["page_content"] for chunk in chunks]
        embeddings = []
        
        for i, text in enumerate(texts):
            if i % 5 == 0:  # Log progress every 5 chunks
                print(f"📊 Processing chunk {i+1}/{len(texts)}")
            
            embedding = self.get_titan_embedding(text)
            if embedding:
                embeddings.append(embedding)
            else:
                # Fallback: zero vector với kích thước mặc định của Titan
                embeddings.append([0.0] * 1536)
        
        return {
            'chunks': chunks,
            'texts': texts,
            'embeddings': embeddings
        }
    
    def similarity_search(self, vector_store, query, k=3):
        """Tìm các chunk liên quan nhất bằng cosine similarity"""
        # Lấy embedding cho query
        query_embedding = self.get_titan_embedding(query)
        if not query_embedding:
            print("❌ Failed to get query embedding, using fallback search")
            return self.fallback_search(vector_store, query, k)
        
        # Tính similarity với tất cả chunks
        similarities = []
        for i, emb in enumerate(vector_store['embeddings']):
            sim = self.cosine_similarity(query_embedding, emb)
            similarities.append((i, sim))
        
        # Sắp xếp theo similarity giảm dần
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Lấy top k chunks
        relevant_chunks = []
        for idx, score in similarities[:k]:
            if idx < len(vector_store['chunks']) and score > 0:  # Chỉ lấy chunks có similarity > 0
                relevant_chunks.append(vector_store['chunks'][idx])
        
        print(f"🔍 Found {len(relevant_chunks)} relevant chunks (best similarity: {similarities[0][1] if similarities else 0:.3f})")
        return relevant_chunks
    
    def fallback_search(self, vector_store, query, k=3):
        """Fallback search khi không có embeddings"""
        print("🔄 Using fallback keyword search")
        query_lower = query.lower()
        
        scores = []
        for i, text in enumerate(vector_store['texts']):
            score = text.lower().count(query_lower)
            scores.append((i, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        relevant_chunks = []
        for idx, score in scores[:k]:
            if score > 0:  # Chỉ lấy chunks có keyword match
                relevant_chunks.append(vector_store['chunks'][idx])
        
        return relevant_chunks
    
    def answer_question(self, vector_store, question):
        """Trả lời câu hỏi dựa trên RAG"""
        print(f"🔍 Searching for relevant content for: {question}")
        
        # Tìm các chunk liên quan
        relevant_chunks = self.similarity_search(vector_store, question, k=3)
        
        if not relevant_chunks:
            return "Không tìm thấy thông tin liên quan trong tài liệu. Vui lòng thử câu hỏi khác hoặc tải lên tài liệu phù hợp hơn."
        
        # Xây dựng context
        context = "\n\n".join([
            f"Đoạn {i+1}: {chunk['page_content']}" 
            for i, chunk in enumerate(relevant_chunks)
        ])
        
        # Tạo prompt cho RAG
        prompt = f"""
        Hãy đọc kỹ các đoạn văn bản sau từ tài liệu:

        {context}

        Dựa TRÊN các đoạn văn bản trên, hãy trả lời câu hỏi sau:
        Câu hỏi: {question}

        YÊU CẦU QUAN TRỌNG:
        - CHỈ sử dụng thông tin từ các đoạn văn bản trên
        - KHÔNG sử dụng kiến thức bên ngoài
        - Nếu không đủ thông tin để trả lời, hãy nói rõ: "Không có đủ thông tin trong tài liệu để trả lời câu hỏi này"
        - Trả lời bằng tiếng Việt, rõ ràng và chi tiết
        - Giữ nguyên tên riêng, thuật ngữ chuyên môn từ tài liệu gốc

        Trả lời:
        """
        
        print("🤖 Generating answer with Bedrock...")
        
        # Ưu tiên dùng Titan (free), fallback Claude
        answer = self.invoke_titan(prompt)
        if not answer:
            answer = self.invoke_claude(prompt)
        
        if not answer:
            return "Xin lỗi, tôi không thể tạo câu trả lời ngay lúc này. Vui lòng thử lại sau."
        
        # Clean answer
        answer = answer.strip()
        if answer.startswith('"') and answer.endswith('"'):
            answer = answer[1:-1]
            
        return answer

# Global instance
bedrock_rag = BedrockRAG()

# Test function để debug local
if __name__ == "__main__":
    # Test embedding
    rag = BedrockRAG()
    test_text = "Xin chào, đây là test"
    embedding = rag.get_titan_embedding(test_text)
    print(f"Embedding test: {len(embedding) if embedding else 'FAILED'}")
    
    # Test generation
    response = rag.invoke_titan("Giới thiệu ngắn về AWS")
    print(f"Generation test: {response[:100] if response else 'FAILED'}")