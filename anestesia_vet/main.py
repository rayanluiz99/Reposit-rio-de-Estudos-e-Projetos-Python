from database.engine import engine
from database.engine import criar_db_e_tabelas
from sqlmodel import Session
from controllers.config_infusao_controller import *
from controllers.farmaco_controller import importar_farmacos_csv

importar_farmacos_csv()