# Document QA với AWS Bedrock

Ứng dụng hỏi đáp tài liệu thông minh sử dụng AWS Bedrock RAG (Retrieval Augmented Generation).

## 🚀 Đã triển khai thành công!

### URLs:
- **Website**: http://docqa-website-dev.s3-website-us-east-1.amazonaws.com
- **API**: https://xy4iztykoa.execute-api.us-east-1.amazonaws.com/dev

### Endpoints API:
- `POST /presign` - Tạo presigned URL để upload file
- `POST /upload` - Xử lý tài liệu đã upload
- `POST /ask` - Hỏi đáp với AI

## 🎯 Tính năng

✅ **Upload tài liệu**: Hỗ trợ PDF và TXT  
✅ **AI Processing**: Sử dụng Amazon Titan (miễn phí)  
✅ **Vector Search**: Tìm kiếm ngữ nghĩa với embeddings  
✅ **RAG**: Trả lời dựa trên nội dung tài liệu  
✅ **Session Management**: Lưu trữ tạm thời 24h  
✅ **CORS**: Hỗ trợ cross-origin requests  

## 🛠️ Kiến trúc

```
Frontend (S3) → API Gateway → Lambda → Bedrock
                    ↓
                DynamoDB + S3 (Storage)
```

## 💰 Chi phí ước tính (tháng)

- **Bedrock Titan**: ~$0 (free tier)
- **Lambda**: ~$0.20/1M requests  
- **S3**: ~$0.023/GB
- **DynamoDB**: ~$0.25/1M requests
- **API Gateway**: ~$3.50/1M requests

**Tổng**: < $5/tháng cho usage thấp

## 🧪 Test ứng dụng

1. Truy cập: http://docqa-website-dev.s3-website-us-east-1.amazonaws.com
2. Upload file `test-document.txt` (đã tạo sẵn)
3. Hỏi: "AWS Bedrock là gì?"
4. Hỏi: "Các tính năng chính của Bedrock?"

## 🔧 Cấu hình AWS

Đảm bảo AWS account có quyền:
- Bedrock model access (us-east-1)
- Lambda, API Gateway, S3, DynamoDB
- IAM permissions

## 📝 Logs & Debug

```bash
# Xem logs Lambda
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/docqa"

# Xem logs realtime
serverless logs -f ask -t
```

## 🔄 Update & Deploy

```bash
# Backend
cd be
serverless deploy

# Frontend  
aws s3 sync fe/ s3://docqa-website-dev --delete
```

## 🎉 Hoàn thành!

Ứng dụng Document QA đã sẵn sàng sử dụng với đầy đủ tính năng AI-powered document analysis!