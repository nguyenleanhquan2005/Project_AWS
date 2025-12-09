---
title: "Proposal"
date: "2025-12-01"
weight: 2
chapter: false
pre: " <b> 2. </b> "
---

# Document QA with AWS Bedrock

## Intelligent Document Analysis System using RAG

### 1. Executive Summary

The Document QA system is a serverless application designed to revolutionize how users interact with documents. By leveraging **AWS Bedrock** for Generative AI and **RAG (Retrieval Augmented Generation)** technology, the platform allows users to upload PDF/TXT documents and ask natural language questions. The system provides accurate, context-aware answers by retrieving relevant information from the uploaded documents, significantly reducing manual search time and improving information accessibility.

### 2. Problem Statement

### What's the Problem?

Traditional document search methods (keyword matching) often fail to capture context or semantic meaning. Manual document review is time-consuming, error-prone, and inefficient, especially for large volumes of text. Users struggle to extract specific insights quickly, leading to productivity bottlenecks.

### The Solution

We propose a **Serverless RAG-based Chatbot** using **AWS Bedrock (Amazon Titan)**. The solution involves:

- **Upload & Processing**: Users upload documents to S3; Lambda functions trigger text extraction and embedding generation.
- **Vector Search**: Embeddings are stored and queried to find relevant document chunks.
- **Generative AI**: AWS Bedrock generates natural language responses based on the retrieved context.
- **Serverless Architecture**: Built on AWS Lambda, API Gateway, and DynamoDB for automatic scaling and cost efficiency.

### Benefits and Return on Investment

- **Efficiency**: Reduces document analysis time from hours to seconds.
- **Accuracy**: RAG ensures answers are grounded in the provided document, minimizing hallucinations.
- **Cost-Effective**: Serverless pay-as-you-go model (estimated < $5/month for low usage).
- **Scalability**: Automatically handles varying loads without manual infrastructure management.

### 3. Solution Architecture

The platform employs a modern serverless architecture to ensure scalability, security, and performance.

![Architecture](/images/image_proposal.png)
### AWS Services Used

- **AWS Bedrock**: Provides the Foundation Models (Amazon Titan) for embeddings and text generation.
- **AWS Lambda**: Serverless compute for handling API requests, document processing, and orchestration.
- **Amazon API Gateway**: Manages REST API endpoints for the frontend.
- **Amazon S3**: Stores raw uploaded documents and frontend static assets.
- **Amazon DynamoDB**: Manages user sessions and chat history.
- **Vector Store**: (Implemented via Lambda/Local or dedicated vector DB) Stores document embeddings for semantic search.

### Component Design

- **Frontend**: Hosted on S3 (or Amplify), providing a user-friendly chat interface.
- **API Layer**: API Gateway routes requests (`/upload`, `/ask`) to Lambda functions.
- **Processing Layer**: Lambda handles text extraction, calls Bedrock for embeddings, and performs vector similarity search.
- **AI Layer**: AWS Bedrock generates responses using the retrieved context and user query.

### 4. Technical Implementation

**Implementation Phases**

- **Phase 1: Foundation (Weeks 1-4)**: Setup AWS environment, Bedrock access, and basic backend logic.
- **Phase 2: API & Security (Weeks 5-7)**: Develop API Gateway, Lambda functions, and implement CORS/Security.
- **Phase 3: Frontend Development (Weeks 8-11)**: Build the React/Next.js interface and integrate with APIs.
- **Phase 4: Testing & Deployment (Weeks 12-14)**: End-to-end testing, optimization, and final deployment.

**Technical Requirements**

- **AI Model**: Amazon Titan (via Bedrock) for Embeddings and Text Generation.
- **Backend**: Node.js/Python on AWS Lambda.
- **Infrastructure as Code**: Serverless Framework or AWS CDK.
- **Frontend**: React.js / Next.js.

### 5. Timeline & Milestones

- **Month 1**: Architecture Design, AWS Setup, Backend Core (Upload/Embeddings).
- **Month 2**: RAG Implementation, Vector Search Logic, API Development.
- **Month 3**: Frontend Integration, UI/UX Polish, Testing, and Launch.

### 6. Budget Estimation

**Estimated Monthly Costs (Low-Medium Usage)**

- **AWS Bedrock (Titan)**: ~$0 (Free Tier / Low cost per 1k tokens)
- **AWS Lambda**: ~$0.20 per 1M requests
- **Amazon S3**: ~$0.023 per GB
- **Amazon DynamoDB**: ~$0.25 per 1M requests
- **Amazon API Gateway**: ~$3.50 per 1M requests

**Total Estimated**: < **$5.00 / month**

### 7. Risk Assessment

#### Risk Matrix

- **Hallucinations (AI Errors)**: Medium Impact, Medium Probability.
- **Cost Overruns**: Medium Impact, Low Probability (Serverless).
- **Data Leakage**: High Impact, Low Probability.

#### Mitigation Strategies

- **Hallucinations**: Strict RAG implementation (grounding answers in context).
- **Cost**: Set AWS Budget Alerts and usage quotas.
- **Security**: Use Presigned URLs for S3, IAM roles with least privilege.

### 8. Expected Outcomes

#### Technical Improvements

- Fully automated document analysis pipeline.
- Sub-second retrieval latency for vector search.
- Scalable architecture supporting concurrent users.

#### Long-term Value

- A reusable RAG framework for future knowledge base applications.
- Significant productivity gains for users needing quick information retrieval.


### 9. Team Structure and Responsibilities

| Name | Student ID | Primary Role | Email/Contact Info |
|------|-----------|--------------|-------------------|
| **Nguyễn Lê Anh Quân** | SE192307 | Team Leader/ Cloud Architect | nguyenleanhquan2005@gmail.com |
| **Đào Quang Vinh** | SE180012 | Project Manager/ Backend Developer (Bedrock, RAG) | its.vnhdq@gmail.com |
| **Nguyễn Thanh Liêm** | SE184163 | Backend Developer | liemntse184163@fpt.edu.vn |
| **Trần Đình Phong** | SE184217 | Frontend Developer/ UI/UX Designer | phongtdse184217@fpt.edu.vn |
| **Dương Nguyễn Gia Huy** | SE182202 | QA Engineer/Backend Developer (Bedrock, RAG) | huydngse182202@fpt.edu.vn |


####  Detailed Responsibilities by Team Member

##### Nguyễn Lê Anh Quân - Cloud Architect/ Team Leader
**Primary Responsibilities:**
- AWS architecture design and service selection
- Infrastructure planning and optimization
- Security architecture and IAM policies
- Technical consultation and best practices

---

##### Đào Quang Vinh - Project Manager/Backend Developer
**Primary Responsibilities:**
- Overall project management and timeline coordination
- Team coordination and task assignment
- Progress reporting to instructor/advisor
- Risk management and mitigation strategies
- Documentation oversight and quality assurance
- Build vector search and retrieval logic
- Develop chat/query handler Lambda function


##### Dương Nguyễn Gia Huy - QA Engineer/Backend Developer
**Primary Responsibilities:**
- Core backend logic development
- Amazon Bedrock integration (Foundation Models)
- RAG (Retrieval-Augmented Generation) pipeline implementation
- Develop Lambda function for document ingestion
- Integrate Amazon Bedrock Knowledge Bases
- Implement text chunking and embedding generation

---

##### Nguyễn Thanh Liêm - Backend Developer 
**Primary Responsibilities:**
- Backend infrastructure and data management
- CI/CD pipeline development
- System monitoring and logging
- Performance optimization
- DynamoDB schema design and implementation
- Conversation history storage logic

---

##### Trần Đình Phong - Frontend Developer
**Primary Responsibilities:**
- User interface design and development
- Frontend-backend integration
- User experience optimization
- Responsive design implementation
- Implement file upload interface with drag-and-drop
- Connect frontend to API Gateway endpoints
- Handle API responses and error states
- Deploy frontend to S3 + CloudFront

---

