# EDITS

Al chequear la cantidad de sujetos en wo_crux contra los anteriores veo que me faltan alrededor de 100 sujetos. Pruebo sacar el assert, tenia unos cuantos sujetos con errores que saque del json, por ejemplo:
`subjs = ["NDARAB348EWR", "NDARAH948UF0", "NDARAN524ZK6", "NDARAP782TVC", "NDARAP785CTE"]`

Entonces despues de sacar el assert pruebo corriendo estoy si viene por aca la falta de sujetos ()
`python3 calculate_nss.py -V 'Diary' -S 'finegrained' -N wo_crux`

Era eso, asi que voy generar de nuevos los archivos sin cruz y volver a correr el join.

# Como correr algunas cosas

```bash
# Unir tablas

python3 join_nss_df.py -V Diary -W wo_crux.csv
# Correr por frames y crear las tablas necesarias
python3 create_frame_tables.py -F 1 -fn results_nss_diary_wo_crux.csv 

# Correr para escenas y crear las tablas necesarias
python3 create_frame_tables.py -F 1 -S True -fn results_nss_diary_wo_crux.csv 
```

# Donde encontrar los colabs de otros scripts usados

- Como correr los modelos de saliencia
- Como slicear y guardar los frames
- Como crear los Ground Truth
- Como se calcularon los cortes y los features de las escenas