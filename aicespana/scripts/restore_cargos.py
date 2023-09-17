import aicespana.models
import os


"""
    The script is applicable for restoring back the relation of personal externo
    that were delete when changing the foreignKey to many to many relation.
    This script will populate again the relations
"""

def run():
    w_dir = os.getcwd()
    up_dir = "/".join(w_dir.split("/")[:-1])
    f_name = os.path.join(up_dir, "cargos_voluntarios.csv")
    with open(f_name, "r") as fh:
        lines = fh.readlines()
    for line in lines[1:]:
        per_id, cargo_id = line.strip().split(",")
        aicespana.models.PersonalExterno.objects.get(pk__exact=per_id).cargo.add(aicespana.models.Cargo.objects.get(pk__exact=cargo_id))
    
    
    f_name = os.path.join(up_dir, "cargos_iglesia.csv")
    with open(f_name, "r") as fh:
        lines = fh.readlines()
    for line in lines[1:]:
        per_ig_id, cargo_ig_id = line.strip().split(",")
        aicespana.models.PersonalIglesia.objects.get(pk__exact=per_ig_id).cargo.add(aicespana.models.Cargo.objects.get(pk__exact=cargo_ig_id))
    print ("completed")