# bali-cli

Github: https://github.com/bali-framework/bali-cli

<img src="https://img.shields.io/pypi/v/bali-cli" />

<p align="center">
    <b>bali-cli</b> is 
    CLI tools to simplify gRPC services and clients
</p>

## Cli commands 

**bali add {service}**

> Add service to clients folder

```bash
# Add user service client to current project
# run the command in project root directory
bali add user
```

**bali build**

> Build current development service protobuf 
>
> Protobuf Path: /services/rpc/*.proto

```bash
# build gRPC pb2 and pb2_grpc files 
# run the command in project root directory
bali build
```
