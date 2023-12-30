
from pydantic import BaseModel,Field,ConfigDict
from typing import Optional

def create_pydantic(namespace:dict=None,suffix:str='API'):
    if namespace is None:
        namespace = globals()
    def create_pydantic_inner(original_class):
        def _filter_for_no_default(n,val):
            return not n.startswith('_') and ('default' not in val.__dict__ or not val.default)
        
        def _filter_for_default(n,val):
            return not n.startswith('_') and (val.primary_key or ('default'  in val.__dict__ and val.default))
        if not original_class.__name__+suffix in namespace:
            print('INFO: add an empty class with the name '+original_class.__name__+suffix,' to avoid errors')
        namespace[original_class.__name__+suffix] = type(
            original_class.__name__+suffix,
            (BaseModel,),
            {
                '__module__': original_class.__module__,
                'model_config' : ConfigDict(from_attributes=True),
                '__annotations__':{
                    n:val.__args__[0]
                    for n,val in original_class.__annotations__.items()
                    if not original_class.__dict__[n].primary_key
                }|{
                    n:Optional[val.__args__[0] ]
                    for n,val in original_class.__annotations__.items()
                    if original_class.__dict__[n].primary_key
                },
            }|{
                n:Field()
                for n,val in original_class.__dict__.items()
                if _filter_for_no_default(n,val)
            }|{
                n:Field(default=val.default.arg if 'default' in val.__dict__ and val.default else None)
                for n,val in original_class.__dict__.items()
                if _filter_for_default(n,val)
            }
        )
        
        return original_class
    return create_pydantic_inner