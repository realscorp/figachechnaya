kubectl create secret generic history \
  --from-literal=db_login=$DB_LOGIN \
  --from-literal=db_password=$DB_PASS