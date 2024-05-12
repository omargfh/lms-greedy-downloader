

from dataclasses import dataclass

@dataclass
class CrawlerConfig:
    user_id: int
    canvas_domain: int
    output: str
    curl_path: str
    skip_download: bool = False
    use_threads: bool = False


@dataclass
class CanvasCrawlOptions:
    include_user_root_target: bool = True
    include_courses: bool = True
    include_groups: bool = True
    include_modules: bool = True
    courses: list = None

@dataclass
class CanvasFileSystemResponse:
    id: int
    name: str
    full_name: str

    context_id: int
    context_type: str

    parent_folder_id: int

    created_at: str
    updated_at: str

    lock_at: str
    unlock_at: str

    position: any
    can_upload: bool

    for_submissions: bool

    locked: bool
    files_count: int
    folders_count: int
    locked_for_user: bool
    hidden_for_user: bool

    hidden: bool

    folders_url: str
    files_url: str

    errors: any = None

    def __getitem__(self, key):
        return getattr(self, key)