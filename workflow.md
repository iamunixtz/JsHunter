# JSHunter Workflow Diagram

```mermaid
graph TB
    %% User Input Layer
    A[User Input] --> B{Input Type}
    B -->|CLI| C[Command Line Interface]
    B -->|Telegram| D[Telegram Bot]
    B -->|Discord| E[Discord Bot]
    B -->|Web GUI| F[Web Interface]
    
    %% Configuration Layer
    G[Configuration] --> H[Bot Tokens]
    G --> I[Performance Settings]
    G --> J[Discord Webhook]
    
    %% Core Processing Layer
    C --> K[JSHunter Core Engine]
    D --> K
    E --> K
    F --> K
    
    %% High-Performance Processing
    K --> L{Performance Mode}
    L -->|High-Performance| M[Async Download Manager]
    L -->|Legacy| N[Sequential Processing]
    
    %% Download & Processing
    M --> O[Concurrent Downloads<br/>200+ simultaneous]
    O --> P[Batch File Processing]
    P --> Q[TruffleHog Scanner<br/>Parallel Execution]
    
    %% Secret Detection
    Q --> R[Secret Detection Engine]
    R --> S{Secret Found?}
    S -->|Yes| T[Verify Secret]
    S -->|No| U[Continue Processing]
    
    %% Verification & Classification
    T --> V{Verification Status}
    V -->|Verified| W[High-Confidence Secret]
    V -->|Unverified| X[Potential Secret]
    
    %% Result Processing
    W --> Y[Result Aggregation]
    X --> Y
    U --> Y
    
    %% Output Generation
    Y --> Z[Generate Results]
    Z --> AA[Verified Results JSON]
    Z --> BB[Unverified Results JSON]
    Z --> CC[Formatted Messages]
    
    %% Notification Layer
    AA --> DD{Notification Type}
    BB --> DD
    CC --> DD
    
    DD -->|Discord| EE[Discord Webhook<br/>Immediate Alerts]
    DD -->|Telegram| FF[Telegram Messages<br/>File Attachments]
    DD -->|CLI| GG[Console Output<br/>Progress Tracking]
    DD -->|Web| HH[Web Dashboard<br/>Real-time Updates]
    
    %% File Management
    EE --> II[File Cleanup]
    FF --> II
    GG --> II
    HH --> II
    
    %% Performance Monitoring
    K --> JJ[Progress Tracker]
    JJ --> KK[Real-time Stats<br/>ETA Calculation<br/>Rate Monitoring]
    
    %% Error Handling
    M --> LL[Error Recovery]
    N --> LL
    LL --> MM[Retry Logic<br/>Fallback Processing]
    
    %% Styling
    classDef userInput fill:#e1f5fe
    classDef processing fill:#f3e5f5
    classDef output fill:#e8f5e8
    classDef notification fill:#fff3e0
    classDef performance fill:#fce4ec
    
    class A,B,C,D,E,F userInput
    class K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,AA,BB,CC processing
    class DD,EE,FF,GG,HH output
    class II,LL,MM notification
    class JJ,KK performance
```

## Workflow Description

### 1. **Input Layer**
- **CLI**: Direct command-line usage with file or URL input
- **Telegram Bot**: Interactive bot with `/scanurl` and file upload commands
- **Discord Bot**: Server-based bot with `!scanurl` and file attachment support
- **Web GUI**: Browser-based interface for easy access

### 2. **Configuration Management**
- Bot tokens and API keys stored securely
- Performance tuning parameters
- Discord webhook URLs for notifications

### 3. **Core Processing Engine**
- **High-Performance Mode**: Async downloads, parallel processing, batch operations
- **Legacy Mode**: Sequential processing for small batches
- **Adaptive Selection**: Automatically chooses optimal mode based on input size

### 4. **Download & Processing Pipeline**
- **Concurrent Downloads**: 200+ simultaneous HTTP requests
- **Batch Processing**: Groups files for efficient TruffleHog scanning
- **Parallel Execution**: Multiple TruffleHog instances running simultaneously

### 5. **Secret Detection & Verification**
- **TruffleHog Integration**: Industry-standard secret detection
- **Verification Process**: API validation for high-confidence results
- **Classification**: Separates verified from unverified findings

### 6. **Result Generation**
- **JSON Output**: Structured data for programmatic access
- **Formatted Messages**: Human-readable output with full API keys
- **File Attachments**: Complete result files for detailed analysis

### 7. **Multi-Channel Notifications**
- **Discord**: Immediate webhook alerts for verified secrets
- **Telegram**: Rich messages with file attachments
- **CLI**: Real-time progress and console output
- **Web**: Live dashboard updates

### 8. **Performance Monitoring**
- **Real-time Stats**: Progress tracking with ETA
- **Rate Monitoring**: Throughput and success rate metrics
- **Error Recovery**: Automatic retry and fallback mechanisms

### 9. **Resource Management**
- **File Cleanup**: Automatic removal of temporary files
- **Memory Optimization**: Efficient handling of large datasets
- **Connection Pooling**: Optimized HTTP client management
