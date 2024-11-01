import redis

def connect_to_redis_server():
    # Redis 연결 정보
    redis_host = "redis-server-master.default.svc.cluster.local"  # Redis 서비스 이>름
    redis_port = 6379  # 기본 포트
    redis_password = "OB7CI0ekrz"

    return (
        redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True  # 반환값을 문자열로 디코딩
        )
    )
