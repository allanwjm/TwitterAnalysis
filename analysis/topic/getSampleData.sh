for year in '2014' '2015' '2016' '2017' '2018'
do
for city in 'melbourne' 'sydney' 'perth' 'brisbane' 'adelaide' 'canberra' 'hobart'
do
for day in '0' '1' '2' '3' '4' '5' '6'
do
nohup python3 getSampleData.py $year $city $day &
done
done
done
