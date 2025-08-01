# Adicione no início do arquivo:
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Agora importe normalmente


# Adiciona o diretório raiz ao path do Python
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Agora importe normalmente
from database.engine import engine, criar_db_e_tabelas
from models.sessao import SessaoAnestesia
from models.config_infusao import ConfigInfusao
from models.animal import Animal
from models.farmaco import Farmaco
from controllers import (
    animal_controller,
    farmaco_controller,
    sessao_controller,
    config_infusao_controller
)

import unittest
from sqlmodel import Session, select

class TestSistemaAnestesia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        criar_db_e_tabelas()
        cls.session = Session(engine)
        
        

class TestSistemaAnestesia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Prepara o banco de dados de teste"""
        criar_db_e_tabelas()
        cls.session = Session(engine)
        
        # Dados de teste
        cls.animal_teste = Animal(
            nome="Rex", 
            especie="Cão", 
            peso_kg=10.0
        )
        cls.farmaco_bolus = Farmaco(
            nome="Propofol Teste",
            dose=4.0,
            concentracao=10.0,
            unidade_dose="mg/kg",
            modo_uso="bolus"
        )
        cls.farmaco_infusao = Farmaco(
            nome="Remifentanil Teste",
            dose=5.0,
            concentracao=0.5,
            unidade_dose="µg/kg/h",
            modo_uso="infusão contínua"
        )

    def setUp(self):
        """Executado antes de cada teste"""
        self.session.add_all([
            self.animal_teste, 
            self.farmaco_bolus,
            self.farmaco_infusao
        ])
        self.session.commit()

    def tearDown(self):
        """Executado após cada teste"""
        self.session.rollback()
        for table in [SessaoAnestesia, ConfigInfusao, Animal, Farmaco]:
            self.session.exec(select(table)).delete()
        self.session.commit()

    # --- TESTES PRINCIPAIS ---
    def test_1_cadastro_animal(self):
        """Testa o cadastro básico de animais"""
        animal_controller.cadastrar_animal("Thor", "Gato", 4.5)
        animal = self.session.exec(
            select(Animal).where(Animal.nome == "Thor")
        ).first()
        self.assertEqual(animal.peso_kg, 4.5)

    def test_2_cadastro_farmaco(self):
        """Testa o cadastro de fármacos"""
        farmaco_controller.cadastrar_farmaco(
            "Ketamina Teste", 5.0, 100.0, "mg/kg", "bolus"
        )
        farmaco = self.session.exec(
            select(Farmaco).where(Farmaco.nome == "Ketamina Teste")
        ).first()
        self.assertEqual(farmaco.concentracao, 100.0)

    def test_3_config_infusao(self):
        """Testa os cálculos de infusão"""
        config = config_infusao_controller.criar_config_infusao(
            self.session, peso_kg=15.0, volume_bolsa=250
        )
        taxas = config_infusao_controller.calcular_taxas(config)
        self.assertAlmostEqual(taxas['taxa_ml_h'], 15.0)  # 1 ml/kg/h * 15 kg

    def test_4_sessao_bolus(self):
        """Testa registro de sessão com bolus"""
        sessao_id = sessao_controller.registrar_sessao(
            self.animal_teste.id, 
            self.farmaco_bolus.id,
            peso_kg=None  # Usa do animal
        )
        sessao = self.session.get(SessaoAnestesia, sessao_id)
        dose_esperada = (10.0 * 4.0) / 10.0  # peso * dose / concentração
        self.assertAlmostEqual(sessao.dose_utilizada_ml, dose_esperada)

    def test_5_sessao_infusao(self):
        """Testa registro de sessão com infusão"""
        config = config_infusao_controller.criar_config_infusao(
            self.session, peso_kg=10.0, volume_bolsa=100
        )
        sessao_id = sessao_controller.registrar_sessao(
            self.animal_teste.id,
            self.farmaco_infusao.id,
            peso_kg=None,
            config_infusao_id=config.id
        )
        sessao = self.session.get(SessaoAnestesia, sessao_id)
        self.assertEqual(sessao.config_infusao_id, config.id)

    def test_6_prescricao_txt(self):
        """Testa geração de prescrição"""
        sessao_id = sessao_controller.registrar_sessao(
            self.animal_teste.id,
            self.farmaco_bolus.id
        )
        sessao_controller.gerar_prescricao_txt(sessao_id)
        
        import os
        self.assertTrue(
            os.path.exists(f"prescricoes/prescricao_{sessao_id}.txt")
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)