# Для удобства локальной отработки, пока нет CI/CD
# Просто сделай: source env-setup-example.sh

export DB_HOST=postgresql.mcs.local
export DB_PORT=5432
export DB_NAME=history
export DB_LOGIN=history
export DB_PASS=**************
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

export TF_VAR_postgresql_db_name=$DB_LOGIN
export TF_VAR_postgresql_db_user=$DB_PASS
export TF_VAR_postgresql_db_pass=$DB_PASS
