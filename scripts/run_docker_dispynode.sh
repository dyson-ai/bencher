docker build -t dispy .

while :; do
    docker run --net=host -it dispy dispynode.py --serve 1
done
# docker run --net=host -it dispy