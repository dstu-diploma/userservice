generate-auth-grpc:
	python -m grpc_tools.protoc \
  -I=./proto \
  --python_out=./app/grpc/auth/ \
  --grpc_python_out=./app/grpc/auth/ \
  --mypy_out=./app/grpc/auth/ \
  ./proto/auth.proto
