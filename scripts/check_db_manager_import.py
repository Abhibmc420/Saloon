import importlib
m = importlib.import_module('db_manager')
print('User in m:', 'User' in m.__dict__)
print('User:', getattr(m,'User', None))
print('DatabaseUserManager:', getattr(m,'DatabaseUserManager', None))
print('Done')
