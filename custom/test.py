def getParams():
    params = {
        "param1" : {
            "text" : "Custom test",
            "type" : "checkbox",
            "params" : {
                "checked" : False
            }      
        }
    }
    
    return params
    
def getAttribs():
    attributes = {
        "in0" : {
            "index" : -1,
            "preset" : "attr_preset_1",
            "plug" : False,
            "socket" : True,
            "type" : "int"
        },
        "in1" : {
            "index" : -1,
            "preset" : "attr_preset_1",
            "plug" : False,
            "socket" : True,
            "type" : "int"
        }
    }
    
    return attributes