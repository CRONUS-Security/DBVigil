# Docker 部署可测试 UDF 的 MySQL 容器指南

本指南帮助你在本地通过 Docker 快速部署一个**可用于 UDF 提权测试**的 MySQL 容器。

## 1. 关键配置说明

- **必须关闭** `--secure-file-priv`，否则无法写入 UDF 文件。
- 推荐使用 MySQL 5.7 或 8.0 低安全配置镜像。
- 需开放 3306 端口。
- 建议设置 root 密码为 `root` 方便测试。

## 2. 推荐启动命令

```sh
# 拉取官方 MySQL 8.0 镜像（如需 5.7 可改版本号）
docker pull mysql:8.0

# 启动容器（关闭 secure-file-priv，允许 UDF 写入）
docker run -d \
  --name mysql-udf-test \
  -e MYSQL_ROOT_PASSWORD=root \
  -p 3306:3306 \
  -v mysql_udf_data:/var/lib/mysql \
  mysql:8.0 \
  --default-authentication-plugin=mysql_native_password \
  --secure-file-priv="" \
  --plugin-load-add=""
```

- `--secure-file-priv=""` 关闭文件写入限制。
- `--plugin-load-add=""` 避免部分镜像默认加载插件导致冲突。

## 3. 进入容器

```sh
docker exec -it mysql-udf-test bash
```

## 4. 容器内常用路径

- 插件目录（常见）：`/usr/lib/mysql/plugin/` 或 `/usr/lib64/mysql/plugin/`
- 数据目录：`/var/lib/mysql`

## 5. 连接测试

可用 DBVigil 或命令行连接：

```sh
mysql -h 127.0.0.1 -P 3306 -u root -p
# 密码: root
```

## 6. 常见问题

- **1290 错误**：`The MySQL server is running with the --secure-file-priv option so it cannot execute this statement`
  - 说明 `--secure-file-priv` 没有关闭，需用上文命令启动。
- **UDF 写入失败**：确认插件目录权限，必要时 `chmod 777`。

## 7. 停止与清理

```sh
docker stop mysql-udf-test
docker rm mysql-udf-test
docker volume rm mysql_udf_data
```

---

如需更详细的渗透测试环境搭建建议，请联系项目维护者。
