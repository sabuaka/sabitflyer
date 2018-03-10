def error_parser(json_dict):
    
    if 'status' in json_dict.keys():
        errmsg = str(json_dict)
        raise Exception(errmsg)
    else:
        #No error
        return json_dict