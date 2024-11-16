import re

class ServerInfo:
    
    def __init__(self):
        pass    

    def extract_cpu_info(self,output):
        cpu_info = re.search(r'processor\s+(.+)', output)
        if cpu_info:
            return cpu_info.group(1).strip()
        return None

    def extract_memory_info(self,output):
        memory_info = re.search(r'memory\s+(\d+MiB)', output)
        if memory_info:
            return memory_info.group(1).strip()
        return None

    def extract_disk_info(self,output): 
        disk_info = re.search(r'/\s+(\d+[GTMK])\s+(\d+[GTMK])\s+(\d+[GTMK])', output) 
        if disk_info: 
            return disk_info.group(1).strip()
        return None

    def extract_os_info(self,output):
        os_info = re.search(r'Description:\s+(.+)', output)
        if os_info:
            return os_info.group(1).strip()
        return None