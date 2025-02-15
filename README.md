## 公众号文章下载服务（wechatmp2markdown）构建并部署

1. 下载源码：

	```bash
	git clone https://github.com/fengxxc/wechatmp2markdown.git
	```

2. 拷贝[Dockerfile](wechatmp2markdown/Dockerfile)：

	```Dockerfile
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
	```
3. 构建

	```bash
	docker build --network=host -t wechatmp2markdown .
	```
4. 运行

	```bash
	docker run --rm -d --network=host -e PORT=9999 wechatmp2markdown
	```

5. 验证

	```bash
	curl -o test.md http://localhost:9999?url=https://mp.weixin.qq.com/s/nRQZ7JIFEusvy0uSOVix-g&image=url
	```
## 批量下载公众号服务构建及运行

批量下载公众号服务会读取一个文章列表，然后对文章做一些处理

1. 构建

	```bash
	docker build --network=host -t wechat_downloader .
	```
2. 运行
	
	```bash
	docker run --network=host -v /home/grissom/articles:/data wechat_downloader \
	    --downloader-url "http://localhost:9999" \
	    --csv-file "/data/article_lists.csv" \
	    --dir "/data" \
	    --save-processed
	```

	其中 `csv` 文件格式如下：
	
	```csv
	article_url
	https://mp.weixin.qq.com/s/wbdwz_cYWyil1wS5hs10eQ
	https://mp.weixin.qq.com/s/42NrXSCk0BqYyRhw7hxtUg
	https://mp.weixin.qq.com/s/GHdjMLXs7gVfexr6zY2ATw
	https://mp.weixin.qq.com/s/1rNut6i7x278OjRGQbfEVg
	https://mp.weixin.qq.com/s/ePblJ3UFH48PhLur2dxcuA
	https://mp.weixin.qq.com/s/0w_Kf-Bs4v4qu7cfRU8ZzA
	https://mp.weixin.qq.com/s/8T52cTL-SoI_NoleSyTzmg
	https://mp.weixin.qq.com/s/j1Ib2sCRENklT0tMHYt9SQ
	https://mp.weixin.qq.com/s/KyEfMrZ-4s8HQK2MyMzmjg
	https://mp.weixin.qq.com/s/--Fg7irX8YVDurJbD_TkDA
	```

## 分类并提取关键字

在上一步的基础上，对公众号文章进行分类并提取关键字：

1. 构建

    ```bash
    docker build --network=host -t wechat_keywords .
    ```
2. 运行
    
    ```bash	
	docker run --rm --network=host -v /home/grissom/articles:/data wechat_keywords \
	--base_path "/data" \
	--csv_file_name "article_list.csv" \
	--api_type "openai" \
	--api_url "http://127.0.0.1:11434" \
	--api_key "NONE" \
	--llm_model "qwen2.5:7b"
    ```