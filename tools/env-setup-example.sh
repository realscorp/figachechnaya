# Для удобства локальной разработки
# Просто сделай: source env-setup-example.sh
# При работе с пайплайном эти переменные необходимо поместить в переменные CI/CD

export DB_HOST=postgresql.mcs.local
export DB_PORT=5432
export DB_NAME=history
export DB_LOGIN=history
export DB_PASS='**************'
export DB_NAME=history

export HISTORY_APPEND_URL=http://localhost:9000/api/append/
export METRICS_PORT_HISTORY=9090
export METRICS_PORT_FIGALIZE=9091

export OS_AUTH_URL="https://infra.mail.ru:35357/v3/"
export OS_PROJECT_ID="***************************"
export OS_REGION_NAME="RegionOne"
export OS_USER_DOMAIN_NAME="users"
export OS_USERNAME="*********************"
export OS_PASSWORD="*********************"

export S3_BUCKET='figachechnaya'
export S3_PATH='upload/'
export S3_ENDPOINT='http://hb.bizmrg.com'
export S3_FONT_LINK='https://bucket.hb.bizmrg.com/oldstandard.ttf'
export S3_ACCESS_KEY='*********************'
export S3_SECRET_KEY='*************************'

export KAFKA_BOOTSTRAP='localhost:9092'
export KAFKA_TOPIC_NAME='test'
export KAFKA_GROUP_ID='imagizer'

export FIGALIZE_API_PORT=9000
export IMAGIZER_API_PORT=9001

export TF_VAR_postgresql_db_name=$DB_LOGIN
export TF_VAR_postgresql_db_user=$DB_PASS
export TF_VAR_postgresql_db_pass=$DB_PASS

export TF_VAR_prometheus_admin_password='******'
export TF_VAR_grafana_admin_password='******'
export TF_VAR_alertmanager_admin_password='******'

export TF_VAR_registry_username='token-name'
export TF_VAR_registry_password='token'