
"""
Public Key Infrastructure (PKI) for HSM storage with Parsec
"""

import os
import shutil
import subprocess
import random
import traceback
import typing
import yaml
from effective_config import EffectiveConfig

class PKIPARSEC():
    """ Public Key Infrastructure (PKI) for HSM storage with Parsec """

    CERTIFICATE_BAK = 'certificate.bak'
    LABEL_BAK = 'label.bak'

    def __init__(self):
        self._effective_config = EffectiveConfig()
        self._label = self._effective_config.certificate_file_path().split('object=')[1].split(';')[0]
        print(f'Using PKIPARSEC. Parsec object label = {self._label}')
        self._certificate_backup = f'{os.getcwd()}/{PKIPARSEC.CERTIFICATE_BAK}'
        self._label_backup = self._label
        self._label_backup_path = f'{os.getcwd()}/{PKIPARSEC.LABEL_BAK}'
        self._parsec_tool_path = '/home/ggc_user/parsec-tool'

    def create_csr(self) -> typing.Optional[str]:
        """ Creates a certificate signing request from a new private key """
        try:
            # Derive new label name from existing label name.
            label_backup = self._label
            self._label = ''.join(random.choices(label_backup, k=5)) + ''.join(random.choices(label_backup, k=5))

            print(f'Generating new private key using algorithm RSA-2048')
            subprocess.run(
                [
                    self._parsec_tool_path,
                    "create-rsa-key",
                    "--key-name",
                    self._label,
                    "--for-signing"
                ],
                check=True,
            )

            print(f'Generating CSR using new private key')
            new_csr_pem = subprocess.run(
                [
                    self._parsec_tool_path,
                    "create-csr",
                    "--key-name",
                    self._label,
                    "--cn AWS IoT Certificate",
                    "--ou Amazon Web Services",
                    "--o Amazon.com",
                    "--l Seattle",
                    "--st Washington",
                    "--c US"
                ],
                check=True,
                stdout=subprocess.PIPE,
                text=True
            )
        except Exception as error:
            print(f'Error creating the CSR: {repr(error)}.')
            traceback.print_exc()
            new_csr_pem = None

        return new_csr_pem
    
    def rotate(self, new_cert_pem: str) -> bool:
        """ Rotates from the old to new certificate and private key """
        try:
            certificate_file_path = self._effective_config.certificate_file_path().split('=')[1].split(';')[0]

            shutil.copy2(certificate_file_path, self._certificate_backup)
            with open(self._label_backup_path, 'w', encoding='utf-8') as label_bak_file:
                label_bak_file.write(self._label_backup)
            
            with open(certificate_file_path, 'w', encoding='utf-8') as cert_file:
                cert_file.write(new_cert_pem)

            print(f'Updating new object label in the YAML configuration')
            config = self._effective_config.yaml_configuration()
            config['system']['certificateFilePath'] = f'parsec:import={certificate_file_path};object={self._label};type=cert'
            config['system']['privateKeyPath'] = f'parsec:object={self._label};type=private'

            with open(self._effective_config.yaml_file_path(), 'w') as effective_config_file:
                yaml.safe_dump(config, effective_config_file)

            success = True
        except Exception as error:
            print(f'Error rotating the certificate and private key: {repr(error)}.')
            traceback.print_exc()
            success = False

        return success
    
    def rollback(self) -> bool:
        """ Rolls back to the old certificate and private key """
        try:
            certificate_file_path = self._effective_config.certificate_file_path().split('=')[1].split(';')[0]
            with open(self._label_backup_path, 'r', encoding='utf-8') as label_bak_file:
                self._label_backup = label_bak_file.read()

            shutil.copy2(self._certificate_backup, certificate_file_path)

            print(f'Updating old object label in the YAML configuration')
            config = self._effective_config.yaml_configuration()
            config['system']['certificateFilePath'] = f'parsec:import={certificate_file_path};object={self._label_backup};type=cert'
            config['system']['privateKeyPath'] = f'parsec:object={self._label_backup};type=private'

            with open(self._effective_config.yaml_file_path(), 'w') as effective_config_file:
                yaml.safe_dump(config, effective_config_file)

            self.delete_backup()
            success = True
        except Exception as error:
            print(f'Error rolling back the certificate and private key: {repr(error)}.')
            traceback.print_exc()
            success = False

        return success

    def backup_exists(self) -> bool:
        """ Indicates whether the backup certificate and label exists """
        # We expect neither or both to exist. However, if we lost power, rebooted or restarted
        # at an inopportune moment, it may be that only one exists.
        
        return os.path.exists(self._certificate_backup) and os.path.exists(self._label_backup_path)

    def delete_backup(self) -> None:
        """ Deletes the backup certificate and private key """
        try:
            with open(self._label_backup_path, 'r', encoding='utf-8') as label_bak_file:
                self._label_backup = label_bak_file.read()

            subprocess.run(
                [
                    self._parsec_tool_path,
                    "delete-key",
                    "--key-name",
                    self._label_backup,
                ],
                check=True,
            )

            os.remove(self._certificate_backup)
            os.remove(self._label_backup_path)
        except Exception as error:
            print(f'Error deleting backup: {repr(error)}.')
            traceback.print_exc()