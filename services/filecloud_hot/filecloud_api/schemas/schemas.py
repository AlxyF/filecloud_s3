from pathlib import Path
from typing import Dict
import json, jsonref, jsonschema, yaml
from jsonschema import Draft7Validator
import jsonschema

def fetch_openapi_yaml(filename='FileCloudService_S3.yaml', filepath=__file__) -> Dict:
    '''Fetching yaml openapi file and converting it into json
    default filepath is current module location.'''

    with open(Path(filepath).with_name(filename)) as f:
        json_api = jsonref.loads(json.dumps(yaml.safe_load(f)))
        return json_api

def get_scheme(json_api:dict, schema_name:str) -> Dict:
    '''Parsing for certain scheme by name in openapi specification (in json format).'''

    extracted_schema = json_api['components']['schemas'][f'{schema_name}']
    
    # as File is not in the form in a flask request, it will be validated outside scheme
    if schema_name == 'Upload':
        extracted_schema['required'].remove('File')
    return extracted_schema

def get_schema_validator(schema:str) -> Draft7Validator:
    ''' Setup jsonschema validator class
    redefined integer type validation as a string with only integer values.'''

    def is_int(sample: str):
        try:
            int(sample)
            return True
        except ValueError:
            return False

    type_checker = Draft7Validator.TYPE_CHECKER.redefine(u"integer", lambda checker, instance: (is_int(instance)))
    CustomValidator =  jsonschema.validators.extend(Draft7Validator, type_checker=type_checker)
    validator = CustomValidator(schema=schema)
    return validator

def validate_scheme(instance:str, validator:Draft7Validator) -> bool:
    '''Validates json instance against jsonschema validator class.'''
    
    if validator.is_valid(instance):
        return True
    else:
        return [i for i in validator.iter_errors(instance)]
