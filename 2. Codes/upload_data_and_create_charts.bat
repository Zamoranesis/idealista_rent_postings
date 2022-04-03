call C:\Users\danie\anaconda3\Scripts\activate.bat pysandbox
python ".\2. Codes\load_idealista_data_to_BBDD.py"
python ".\2. Codes\create_idealista_renting_chart.py"
conda deactivate
cmd \k
