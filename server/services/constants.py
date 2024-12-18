# Define a global variable
from functools import wraps

shared_object = None

def set_object(obj):
    global shared_object
    shared_object = obj  # Assign the object to the global variable

def get_object():
    return shared_object  # Access the shared object

def socket_emitter(event_name, emit_data_function=None):
    print("Socket Emitter")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res=func(*args, **kwargs)
            print("hahaha", res)
            if emit_data_function:
                data=emit_data_function(args, kwargs, res)
            else: 
                data={"something": "wrong"}
            print("Data", data, event_name)
            get_object().emit(event_name, data)
            # asyncio.run(sio.emit(event_name, data))
            return res
        return wrapper
    return decorator