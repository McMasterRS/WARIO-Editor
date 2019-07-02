def getParams():
    params = '''{
        "textboxExample" : {
            "text"   : "Textbox Example",
            "type"   : "textbox",
            "params" : {
                "text" : "example text"
            }
        },
        "min" : {
            "text"   : "Minimum value",
            "type"   : "spinbox",
            "params" : {
                "minimum" : -2147483648,
                "maximum" : 2147483647,
                "value"   : 0
            }
        },        
        "nodeEnabled" : {
            "text"   : "Enabled",
            "type"   : "checkbox",
            "params" : {
                "checked" : false
            }
        },
        "loadCode" : {
            "text"   : "File Location",
            "type"   : "loadbox",
            "params" : {
                "text" : "file.exe"
            }
        }
    }'''
    
    return params
    
def getAttribs():
    attributes = '''{  
        "Out" : {  
            "index" : -1,  
            "preset" : "attr_preset_1",  
            "plug" : true,  
            "socket" : false,  
            "type" : "int"  
        },
        "In" : {  
            "index" : -1,  
            "preset" : "attr_preset_1",  
            "plug" : false,  
            "socket" : true,  
            "type" : "int"  
        }
    }'''  

    return attributes