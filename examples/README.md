# Generate example's pb2 & pb_grpc files 

Run the bash in examples root 
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. helloworld.proto
```
