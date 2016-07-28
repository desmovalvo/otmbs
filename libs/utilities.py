#!/usr/bin/python

# global requirements
import json

def output_format(request):
    
    """This function is used to determine the 
    desired output format"""

    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return 0
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return 0
    except:
        pass

    return 1


def get_input_data(request):
    
    """This function is used to retrieve a dictionary of 
    the input data"""

    # read data    
    try:
        if request.content_type == "application/json":

            data = json.loads(request.data)
            return data

        else:
            
            data = {}
            for k in request.form.keys():
                data[k] = request.form[k]
            for k in request.args.keys():
                data[k] = request.args[k]
            return data

    except Exception as e:

        print e
        # not a valid json data
        return None


def input_format(request):
    
    """This function is used to determine the 
    desired output format"""

    try:
        if request.headers.has_key('Content-type') and request.headers['Content-type'] == 'application/json':
            return 0
    except:
        pass

    return 1
