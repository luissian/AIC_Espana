import aicespana.models
import os


"""
    The script is applicable for changing the relation of personal externo
    from the foreignKey to many to many relation. Because this change
    all relations are deleted, before changing on database the existing relation
    is collected in a file with pk of personal_externo and the pk of the cargo.
    
"""


def run():
    w_dir = os.getcwd()
    up_dir = "/".join(w_dir.split("/")[:-1])
    # os.chdir(up_dir)
    f_name = os.path.join(up_dir, "cargos_voluntarios.csv")
    p_ext_objs = aicespana.models.PersonalExterno.objects.all().exclude(cargo=None)
    with open(f_name, "w") as fh:
        fh.write("user_id,cargo_id\n")
        for p_ext_obj in p_ext_objs:
            fh.write(str(p_ext_obj.pk) + ","+ str(p_ext_obj.cargo.pk) + "\n")
    f_name = os.path.join(up_dir, "cargos_iglesia.csv")
    p_ext_objs = aicespana.models.PersonalIglesia.objects.all().exclude(cargo=None)
    with open(f_name, "w") as fh:
        fh.write("user_id,cargo_id\n")
        for p_ext_obj in p_ext_objs:
            fh.write(str(p_ext_obj.pk) + ","+ str(p_ext_obj.cargo.pk) + "\n")
    print ("completed")
    