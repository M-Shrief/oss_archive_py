

def format_oss_fullname(owner_username: str, repo_name: str)->str:
    return f"{owner_username}___{repo_name}"

def format_file_name(name_prefix: str, priority:int, file_number: int):
    return f"{name_prefix}-p{priority}-{file_number}"
