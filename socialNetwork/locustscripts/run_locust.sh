
python -m locust --master --expect-workers=3 --master-bind-port=18943 -f $1 &> /dev/null &
python -m locust --worker --master-port=18943 -f $1 &> /dev/null & 
python -m locust --worker --master-port=18943 -f $1 &> /dev/null & 
python -m locust --worker --master-port=18943 -f $1 &> /dev/null &
echo "locust is up and running"
echo "press enter to kill"
read hej

pkill -f "python -m locust" &> /dev/null
