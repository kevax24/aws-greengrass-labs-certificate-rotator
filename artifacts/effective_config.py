# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Greengrass effective configuration
"""

import os
import platform
import yaml

class EffectiveConfig():
    """ Greengrass effective configuration """
    def __init__(self):
        # Get the Greengrass root path from our working directory
        if platform.system() == 'Windows':
            gg_root_path = os.getcwd().split('\\greengrass\\v2')[0]
            file_path = '\\config\\effectiveConfig.yaml'
        else:
            gg_root_path = os.getcwd().split('/greengrass/v2')[0]
            file_path = '/config/effectiveConfig.yaml'

        self._yaml_file_path = f'{gg_root_path}{file_path}'
        with open(self._yaml_file_path, encoding='utf-8') as effective_config_file:
            self._yaml = yaml.safe_load(effective_config_file)

    def yaml_file_path(self) -> str:
        """ YAML file path configuration """
        return self._yaml_file_path
    
    def yaml_configuration(self) -> str:
        """ YAML file configuration """
        return self._yaml

    def certificate_file_path(self) -> str:
        """ Certificate file path configuration """
        return self._yaml['system']['certificateFilePath']

    def private_key_path(self) -> str:
        """ Private key path configuration """
        return self._yaml['system']['privateKeyPath']
