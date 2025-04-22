import os

#TODO Add paths
paper_processing_config={
    "lp_model":{"config":os.path.abspath(os.path.join(os.path.dirname(__file__),"models/config.yaml")),
                "model":os.path.abspath(os.path.join(os.path.dirname(__file__),"models/model_final.pth"))},
    "vl_model":os.path.abspath(os.path.join(os.path.dirname(__file__),"models/qwen2.5_7B_instruct")),
    "text_embedding_model":os.path.abspath(os.path.join(os.path.dirname(__file__),"models/text_model")),
    "image_embedding_model":os.path.abspath(os.path.join(os.path.dirname(__file__),"models/colpali_")),
    "chunking":{
        "model":os.path.abspath(os.path.join(os.path.dirname(__file__),"models/chunking_model")),
        "threshold":"auto",
        "min_sentences":1,
        "chunk_size":100,
        "return_type":"texts"
    }
}

figure_messages = [{"role": "system", "content": [{"type": "text",
                                                       "text": """You are an expert biologist who is responsible for reading and interpreting scientific figures. For a given figure from a scientific paper
         interpret the figure. Do not provide comments on whether the figure is well done or not. Do not provide extra text on describing that you are looking at figure from a scientific figure. 
         Whenever possible very briefly describe each sections of the figure and then give an overall conclusion about what the figure tells us. 
         """}]},
                       {"role": "user", "content": [{"type": "image", "image": None, }], }]

table_message = [{"role": "system", "content": [{"type": "text",
                                                       "text": """You are an expert biologist who is responsible for reading and interpreting scientific tables. For a given table from a scientific paper
             interpret the table. Do not provide comments on whether the table is well done or not. Do not provide extra text on describing that you are looking at table from a scientific publication. 
             Give an overall conclusion about what the tables tells us. 
             """}]},
                       {"role": "user", "content": [{"type": "image", "image": None, }], }]