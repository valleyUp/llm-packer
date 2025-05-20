import os
import uvicorn
import argparse

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Run the LLM Weights Downloader API server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind the server to')
    parser.add_argument('--reload', action='store_true', help='Auto-reload on code changes')
    parser.add_argument('--env-file', type=str, default='.env', help='Path to .env file')
    
    args = parser.parse_args()
    
    # 检查.env文件
    if not os.path.exists(args.env_file):
        print(f"Warning: .env file not found at {args.env_file}, using default settings")
        
    # 启动服务器
    print(f"Starting server at http://{args.host}:{args.port}")
    print("API documentation will be available at /api/docs")
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    ) 