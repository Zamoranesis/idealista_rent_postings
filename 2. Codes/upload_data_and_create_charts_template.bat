call "path to conda activate.bat and environment"
python ".\2. Codes\load_idealista_data_to_BBDD.py"
python ".\2. Codes\create_idealista_renting_chart.py"
conda deactivate
cmd \k
