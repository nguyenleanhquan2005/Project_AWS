import json
import boto3
import base64
import uuid
import tempfile
import os
from datetime import datetime, timedelta
from rag_bedrock import bedrock_rag

# AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DocQASessions')

def upload(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return options_response()
        
    try:
        print("📤 Starting S3-based processing (upload endpoint expects {'s3_key': ...})...")

        body = json.loads(event.get('body') or '{}')
        s3_key = body.get('s3_key')
        if not s3_key:
            return error_response('Missing s3_key in request body')

        # Download file from S3 to /tmp
        tmp_dir = tempfile.gettempdir()
        local_path = os.path.join(tmp_dir, os.path.basename(s3_key))
        s3.download_file(os.environ['S3_BUCKET'], s3_key, local_path)

        filename = os.path.basename(s3_key)
        print(f"🔄 Processing document from S3: {s3_key} -> {local_path}")

        # Process document with Bedrock RAG
        chunks = bedrock_rag.load_and_split_document(local_path)

        # Build lightweight index: compute embeddings via bedrock and store chunks + embeddings
        embeddings = []
        texts = []
        for i, chunk in enumerate(chunks):
            text = chunk["page_content"]
            emb = bedrock_rag.get_titan_embedding(text) or []
            embeddings.append(emb)
            texts.append(text)

        session_id = str(uuid.uuid4())
        index_key = f"vector_stores/{session_id}.json"

        index_obj = {
            'session_id': session_id,
            'filename': filename,
            'chunks_count': len(chunks),
            'texts': texts,
            'embeddings': embeddings,
            'created_at': datetime.now().isoformat()
        }

        s3.put_object(
            Bucket=os.environ['S3_BUCKET'],
            Key=index_key,
            Body=json.dumps(index_obj).encode('utf-8')
        )

        # Store session in DynamoDB
        table.put_item(Item={
            'session_id': session_id,
            'filename': filename,
            'chunks_count': len(chunks),
            's3_key': index_key,
            'created_at': datetime.now().isoformat(),
            'expires_at': int((datetime.now() + timedelta(hours=24)).timestamp())
        })

        # Cleanup local file
        try:
            os.remove(local_path)
        except Exception:
            pass

        return success_response({
            'session_id': session_id,
            'filename': filename,
            'chunks_count': len(chunks),
            'message': 'Document processed and indexed (lightweight).'
        })

    except Exception as e:
        print(f"❌ Upload processing error: {e}")
        return error_response(f"Upload processing failed: {str(e)}")


def presign(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return options_response()
        
    try:
        body = json.loads(event.get('body') or '{}')
        filename = body.get('filename')
        content_type = body.get('content_type', 'application/octet-stream')
        if not filename:
            return error_response('filename is required')

        # Create s3 key
        session_stub = str(uuid.uuid4())[:8]
        s3_key = f"uploads/{session_stub}/{filename}"

        presigned = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': os.environ['S3_BUCKET'], 'Key': s3_key, 'ContentType': content_type},
            ExpiresIn=3600
        )

        return success_response({'upload_url': presigned, 's3_key': s3_key})
    except Exception as e:
        print(f"❌ Presign error: {e}")
        return error_response(str(e))

def ask(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return options_response()
        
    try:
        print("🤖 Processing question...")
        
        body = json.loads(event['body'])
        question = body.get('question', '').strip()
        session_id = body.get('session_id')
        
        if not question:
            return error_response('Question cannot be empty')
        
        if session_id:
            # Document-based question: load index JSON from S3 and do cosine similarity
            print(f"📄 Document question for session: {session_id}")

            response = table.get_item(Key={'session_id': session_id})
            if 'Item' not in response:
                return error_response('Session not found')

            session_data = response['Item']
            index_key = session_data.get('s3_key')
            if not index_key:
                return error_response('Index not found for session')

            # Download index
            tmp_index = os.path.join(tempfile.gettempdir(), f"{session_id}_index.json")
            s3.download_file(os.environ['S3_BUCKET'], index_key, tmp_index)
            with open(tmp_index, 'r', encoding='utf-8') as f:
                index_obj = json.load(f)

            texts = index_obj.get('texts', [])
            embeddings = index_obj.get('embeddings', [])

            # Compute query embedding
            query_emb = bedrock_rag.get_titan_embedding(question)
            top_k = 3
            ranked = []
            if query_emb and embeddings:
                # cosine similarity
                import math
                def cosine(a, b):
                    if not a or not b:
                        return -1
                    dot = sum(x*y for x,y in zip(a,b))
                    norm_a = math.sqrt(sum(x*x for x in a))
                    norm_b = math.sqrt(sum(x*x for x in b))
                    if norm_a==0 or norm_b==0:
                        return -1
                    return dot/(norm_a*norm_b)

                scores = [(i, cosine(query_emb, emb)) for i, emb in enumerate(embeddings)]
                scores = sorted(scores, key=lambda x: x[1], reverse=True)
                ranked = [texts[i] for i,_ in scores[:top_k]]
            else:
                # fallback: simple keyword matching
                q = question.lower()
                scores = []
                for i,t in enumerate(texts):
                    scores.append((i, t.lower().count(q)))
                scores = sorted(scores, key=lambda x: x[1], reverse=True)
                ranked = [texts[i] for i,_ in scores[:top_k]]

            # Build prompt with top_k contexts
            context_text = "\n\n".join(ranked)
            prompt = f"Dựa trên các đoạn sau từ tài liệu:\n\n{context_text}\n\nCâu hỏi: {question}\n\nTrả lời:"

            answer = bedrock_rag.invoke_titan(prompt)
            if not answer:
                answer = bedrock_rag.invoke_claude(prompt)

            return success_response({
                'answer': answer or "Không thể tạo câu trả lời.",
                'used_document': True,
                'filename': session_data.get('filename'),
                'model': 'bedrock-titan'
            })
        else:
            # General question
            print("🌐 General knowledge question")
            answer = bedrock_rag.invoke_titan(question)
            if not answer:
                answer = bedrock_rag.invoke_claude(question)
            
            return success_response({
                'answer': answer or "Sorry, I couldn't generate an answer.",
                'used_document': False,
                'model': 'bedrock-titan'
            })
            
    except Exception as e:
        print(f"❌ Ask error: {str(e)}")
        return error_response(f"Ask failed: {str(e)}")

def success_response(data):
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(data)
    }

def error_response(message):
    return {
        'statusCode': 500,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type', 
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps({'error': message})
    }

def options_response():
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': ''
    }