import os
import json
import logging
import requests
from pathlib import Path

logger = logging.getLogger("mlcenter")
logging.basicConfig(level=logging.INFO)


class MLCenterAPI:
    
    def __init__(self, MLCENTER_URL:str = None,MLCENTER_USERNAME:str = None,MLCENTER_PASSWORD:str = None):
        self.__MLCENTER_URL:str = MLCENTER_URL or os.environ.get('MLCENTER_URL').rstrip('/')
        self.__MLCENTER_USERNAME:str = MLCENTER_USERNAME or os.environ.get('MLCENTER_USERNAME')
        self.__MLCENTER_PASSWORD:str = MLCENTER_PASSWORD or os.environ.get('MLCENTER_PASSWORD')
        self.__TOKEN:str = self.get_token()
        
    def get_token(self):
        try:
            response = requests.post(
                url=self.__MLCENTER_URL + '/auth-token/', 
                headers={'Content-Type': 'application/json'},
                data=json.dumps({'username': self.__MLCENTER_USERNAME, 'password': self.__MLCENTER_PASSWORD})
            )
            response.raise_for_status()
            return response.json()['token']
        except Exception as e:
            logger.error(e)
            return response.status_code, response.text
        
    def create_experiment(self, 
            project_id:str, experiment_name:str, experiment_description:str,
            experiment_tags:str, experiment_metrics:dict, experiment_hyperparameters:dict, experiment_requirements:str
            ):
        
        response = requests.post(
            url=f'{self.__MLCENTER_URL}/api/experiments/{project_id}/',
            headers={'Authorization': f'Token {self.__TOKEN}', 'Content-Type': 'application/json'},
            data=json.dumps({
                'name': experiment_name,
                'description': experiment_description,
                'tags': experiment_tags,
                'metrics': experiment_metrics,
                'hyperparameters': experiment_hyperparameters,
                'requirements': experiment_requirements
                
            })
        )
        
        return response
        
        
    def log_artifact(self, project_id:str, experiment_id:str, artifact_path:str):
        artifact_path_pox = Path(artifact_path)
        
        response = requests.post(
            url=f'{self.__MLCENTER_URL}/api/experiments/{project_id}/{experiment_id}/artifacts/',
            headers={
                'Authorization': f'Token {self.__TOKEN}', 
                'Accept': 'application/json',
            },
            data={
                'name': str(artifact_path_pox.name),
            },
            files=[
                ('artifact', (str(artifact_path_pox.name), open(artifact_path, 'rb'), 'application/octet-stream'))
            ]
           
        )
        return response
    
    
    def get_release_data(self, project_id:str, model_name:str, model_stage:str):
        response = requests.get(
            url=f'{self.__MLCENTER_URL}/api/mlrelease/{project_id}/{model_name}/{model_stage}/',
            headers={
            'Authorization': f'Token {self.__TOKEN}', 
            'Accept': 'application/json',
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
        
    def download_artifact_from_center(self, url:str, download_path:str):
        response = requests.get(url=f'{self.__MLCENTER_URL}{url}')
        file_name = url.split('/')[-1]
        final_path = os.path.join(download_path, file_name)
        
        with open(final_path, 'wb') as f:
            f.write(response.content)
            
        return final_path
    
    def download_artifacts_from_center(self, urls:list, download_path:str):
        
        return [
            self.download_artifact(url, download_path)
            for url in urls
        ]
        
    
    
class MLCenter(MLCenterAPI):
    
    EXPERIMENT_ID = None
    
    def __init__(self, PROJECT_ID:str, MLCENTER_URL=None,MLCENTER_USERNAME=None,MLCENTER_PASSWORD=None):
        super().__init__(MLCENTER_URL,MLCENTER_USERNAME,MLCENTER_PASSWORD)
        self.PROJECT_ID = PROJECT_ID
        
    def create_experiment(self, project_id: str, experiment_name: str, experiment_description: str, experiment_tags: list, experiment_metrics: dict, experiment_hyperparameters: dict, experiment_requirements: str):
        
        experiment_tags = [str(x).replace(',','').strip() for x in experiment_tags]
        experiment_tags = ','.join(experiment_tags)
        
        response = super().create_experiment(project_id, experiment_name, experiment_description, experiment_tags, experiment_metrics, experiment_hyperparameters, experiment_requirements)
        
        if response.status_code == 201:
            self.EXPERIMENT_ID = response.json().get('id')
            
    def log_artifact(self, artifact_path: str):
        if self.EXPERIMENT_ID is None:
            raise ValueError('You must create an experiment first')
        response = super().log_artifact(self.PROJECT_ID, self.EXPERIMENT_ID, artifact_path)
        if response.status_code == 201:
            return True
        else:
            logger.error(f'Error logging artifact: {response.text}')
            return response
        
        
    def download_artifact(self, artifact_name: str, model_name:str, model_stage:str, download_path:str):
        release_data = self.get_release_data(self.PROJECT_ID, model_name, model_stage)
        artifacts = release_data.get('artifacts')
        for artifact in artifacts:
            if artifact.get('name') == artifact_name:
                url = artifact.get('artifact')
                return super().download_artifact_from_center(url, download_path)
            
        raise ValueError(f'Artifact {artifact_name} not found')
    
    def sync_artifacts(self, model_name:str, model_stage:str, download_path:str):
        release_data = self.get_release_data(self.PROJECT_ID, model_name, model_stage)
        artifacts = release_data.get('artifacts',[])
        urls = [artifact.get('artifact') for artifact in artifacts]
        return super().download_artifacts_from_center(urls, download_path)