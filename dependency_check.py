import importlib
import logging
import sys
import pkg_resources
import tomli
from pathlib import Path

def check_dependencies():
    """
    Verifica automaticamente as dependências do projeto.
    Returns:
        tuple: (bool, list) - (True se todas as dependências estão ok, lista de problemas encontrados)
    """
    logging.info("Verificando dependências do projeto...")
    problems = []
    
    try:
        # Lê o arquivo pyproject.toml
        with open("pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
        
        # Obtém as dependências do projeto
        dependencies = pyproject.get("project", {}).get("dependencies", [])
        
        for dep in dependencies:
            # Extrai o nome do pacote e a versão requerida
            pkg_name = dep.split('>=')[0].strip()
            required_version = dep.split('>=')[1].strip() if '>=' in dep else None
            
            try:
                # Tenta importar o módulo
                importlib.import_module(pkg_name.replace('-', '_'))
                
                # Verifica a versão instalada
                if required_version:
                    installed_version = pkg_resources.get_distribution(pkg_name).version
                    if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(required_version):
                        problems.append(
                            f"Versão incompatível de {pkg_name}: instalada={installed_version}, "
                            f"requerida>={required_version}"
                        )
                logging.info(f"✓ {pkg_name} está instalado e funcionando corretamente")
                
            except ImportError:
                problems.append(f"Dependência {pkg_name} não pode ser importada")
            except pkg_resources.DistributionNotFound:
                problems.append(f"Dependência {pkg_name} não está instalada")
            except Exception as e:
                problems.append(f"Erro ao verificar {pkg_name}: {str(e)}")
    
    except Exception as e:
        problems.append(f"Erro ao ler dependências: {str(e)}")
    
    return len(problems) == 0, problems

def format_dependency_report(success: bool, problems: list) -> str:
    """
    Formata o relatório de verificação de dependências.
    """
    if success:
        return "✓ Todas as dependências estão instaladas e funcionando corretamente."
    
    report = ["Problemas encontrados na verificação de dependências:"]
    for problem in problems:
        report.append(f"✗ {problem}")
    return "\n".join(report)
