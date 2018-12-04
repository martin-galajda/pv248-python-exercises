

echo "Hello, World!"
echo "And here goes env variable: " $ENV_VARIABLE
echo "And here QUERY_STRING: " $QUERY_STRING

echo "Content-type" $CONTENT_TYPE
echo "Content-length" $CONTENT_LENGTH
echo "HTTP_REFERER" $HTTP_REFERER

env

less <&0
