count=0
until [$count -eq 1000]
do
./getLDAData.sh
count=`expr $count + 1`
done
