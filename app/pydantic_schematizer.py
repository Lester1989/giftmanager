
from pydantic import BaseModel,Field,ConfigDict
from typing import Optional

def create_pydantic(namespace:dict=None,suffix:str='API',default_type:type=str):
    if namespace is None:
        namespace = globals()
    def create_pydantic_inner(original_class):
        def _filter_for_no_default(n,val):
            return not n.startswith('_') and ('default' not in val.__dict__ or not val.default)

        def _filter_for_default(n,val):
            return not n.startswith('_') and (val.primary_key or ('default'  in val.__dict__ and val.default))

        def _get_attribute_type(attribute_name: str):
            annotation = original_class.__annotations__.get(attribute_name, None)
            result = annotation.__args__[0] if annotation else default_type
            return Optional[result] if attribute_name=='id' else result

        if original_class.__name__ + suffix not in namespace:
            print( f'INFO: add an empty class with the name {original_class.__name__}{suffix} to avoid errors' )

        namespace[original_class.__name__+suffix] = type(
            original_class.__name__+suffix,
            (BaseModel,),
            {
                '__module__': original_class.__module__,
                'model_config' : ConfigDict(from_attributes=True),
                '__annotations__':{
                    n:_get_attribute_type(n)
                    for n in original_class.__dict__
                    if not n.startswith('_')
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