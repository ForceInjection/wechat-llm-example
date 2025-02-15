# 第 1 阶段：构建阶段
FROM golang:1.20-alpine AS builder

# 使用阿里云的 Alpine 镜像源
RUN echo "http://mirrors.aliyun.com/alpine/v3.16/main" > /etc/apk/repositories && \
    echo "http://mirrors.aliyun.com/alpine/v3.16/community" >> /etc/apk/repositories

# 安装 make 命令
RUN apk add --no-cache make

# 设置 Go 代理
ENV GO111MODULE=on
ENV GOPROXY=https://mirrors.aliyun.com/goproxy/,direct

# 设置工作目录
WORKDIR /app

# 复制 go.mod 和 go.sum 文件
COPY go.mod go.sum ./
RUN go mod tidy

# 复制所有代码
COPY . .

# 使用 make 构建
RUN make build-linux

# 第 2 阶段：运行阶段
FROM alpine:latest

# 使用阿里云的 Alpine 镜像源
RUN echo "http://mirrors.aliyun.com/alpine/v3.16/main" > /etc/apk/repositories && \
    echo "http://mirrors.aliyun.com/alpine/v3.16/community" >> /etc/apk/repositories

# 安装必要的运行时依赖
RUN apk --no-cache add ca-certificates

# 设置工作目录
WORKDIR /usr/bin

# 复制构建的二进制文件
COPY --from=builder /app/build/wechatmp2markdown-v1.1.9_linux_amd64 wechatmp2markdown

# 暴露默认端口 8080
EXPOSE 8080

# 使用环境变量来设置端口，默认值为 8080
CMD ["sh", "-c", "wechatmp2markdown server ${PORT:-8080}"]