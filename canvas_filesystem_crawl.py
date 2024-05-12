
import os
import sys
import time
from typing import Tuple

from constants import SEP, ENDL
from console import info, error, success, warning

from canvas_helpers import mkdir_p, ellipsis, course_filter
from canvas_selenium import request_json, download, download_multiple
from canvas_dataclasses import CanvasFileSystemResponse, CanvasCrawlOptions, CrawlerConfig
from canvas_urls import user_courses, user_root, course_groups, course_modules, course_folders, group_folders, module_items
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from canvas_download_loop import download_multiple_async

from enum import Enum

class CanvasCrawlInterfaces(Enum):
    USER="user"
    COURSE="course"
    GROUP="group"
    MODULE="module"

    FILE="file"
    ITEM="item"
    FOLDER="folder"

class CanvasFileSystemCrawl:
    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig):
        self.driver = driver
        self.queue = []
        self.config = config
        self.wait = WebDriverWait(driver, 20)


    def crawl(self, user_id: int = None, fetch_url: Tuple[str, str, CanvasCrawlInterfaces] = None):
        skip_download = self.config.skip_download
        user_id = user_id or self.config.user_id

        fetch_url, cursor, interface = fetch_url

        cursor = os.path.join(self.config.output, "canvas", str(user_id), cursor);

        info(f"Creating directory {cursor}")
        mkdir_p(cursor)

        try:
            folder = request_json(self.driver, fetch_url)
            if ("errors" in folder) or (folder == []):
                error(f"XXX - {folder['errors']}")
                return
        except Exception as e:
            error(f"XXX - {e}")
            return
        success(f"Found folder {folder['name']}")

        self.queue.append(tuple([CanvasFileSystemResponse(**folder), cursor]))
        download_queue = []
        while len(self.queue) > 0:
            try:
                folder, cursor = self.queue.pop(0)
                if folder["errors"] is not None:
                    error(f"XXX - {folder['errors']}")
                    continue
                cursor = os.path.join(cursor, folder['name'])
                info(f"-- Processing folder {folder['name']}")
                mkdir_p(cursor)

                if folder.folders_count > 0:
                    if folder.locked_for_user or folder.hidden_for_user:
                        warning(f"? - {folder['name']} is locked or hidden")
                    response = request_json(self.driver, folder.folders_url)
                    for subfolder in response:
                        success(f"\t* Found subfolder {subfolder['name']}")
                        mkdir_p(os.path.join(cursor, subfolder['name']))

                        self.queue.append((CanvasFileSystemResponse(**subfolder), cursor))
                if folder.files_count > 0:
                    response = request_json(self.driver, folder.files_url)
                    if response == [] or type(response) == dict:
                        warning(f"! - No files found in folder {folder['name']}")
                    else:
                        for file in response:
                            info(f"\t* Added {file['filename']} to download queue. Queue length: {len(download_queue)}.")
                            download_queue.append((f"https://{self.config.canvas_domain}/", file['url'], os.path.join(cursor, file['filename'])))
            except Exception as e:
                error(f"XXX - {e}")
                error(f"XXX - {folder} failed to download")

        if not skip_download:
            if self.config.use_threads:
                download_multiple_async(self.driver, download_queue)
            else:
                download_multiple(self.driver, download_queue)
        else:
            info(f"Skipping download of {len(download_queue)} files due to -skip_download flag set")



    def crawl_all(self, user_id: int, options: CanvasCrawlOptions = CanvasCrawlOptions()):
        info("Crawling Canvas filesystem...")

        domain = self.config.canvas_domain
        user_id = user_id or self.config.user_id


        crawl_targets = [(
            user_root(self.config.canvas_domain, user_id),
            "",
            CanvasCrawlInterfaces.USER
        )] if options.include_user_root_target else []
        success("$ Identified root user folder")
        courses = request_json(self.driver, user_courses(domain, user_id))
        if options.courses:
            info(f"Filtering courses based on {options.courses}")
            courses = filter(course_filter(options.courses), courses)

        courses = list(courses) if courses else []
        for course in courses:
            success(f"\t* Found course {course['name']}")

        for course in courses:
            success(f"$ Processing course {course['name']}")

            if options.include_groups:
                groups = request_json(self.driver, course_groups(domain, course['id']))
                info("Looking for groups...")
                if groups == [] or type(groups) == dict:
                    warning(f"! - No groups found in course {ellipsis(course['name'])}")
                else:
                    for group in groups:
                        info(f"\t* Found group {group['name']} in course {ellipsis(course['name'])}")

                    for group in groups:
                        success(f"$ Processing group {group['name']} in course {ellipsis(course['name'])}")
                        crawl_targets.append((
                            group_folders(domain, group['id']),
                            os.path.join(course['name'], "groups", group['name']),
                            CanvasCrawlInterfaces.GROUP
                        ))

            if options.include_modules:
                modules = request_json(self.driver, course_modules(domain, course['id']))
                info("Looking for modules...")
                if modules == [] or type(modules) == dict:
                    warning(f"! - No modules found in course {ellipsis(course['name'])}")
                else:
                    for module in modules:
                        success(f"\t* Found module {module['name']} in course {ellipsis(course['name'])}")
                    for module in modules:
                        success(f"$ Processing module {module['name']} in course {ellipsis(course['name'])}")
                        crawl_targets.append((
                            module_items(domain, course['id'], module['id']),
                            os.path.join(course['name'], "modules", module['name']),
                            CanvasCrawlInterfaces.MODULE
                        ))

            crawl_targets.append((
                course_folders(domain, course['id']),
                course['name'],
                CanvasCrawlInterfaces.COURSE
            ))

        # path gymnastics
        targets_dir = os    .path.join(self.config.output, "canvas", str(user_id))
        targets_fname = f"targets-{user_id}-{time.time().__str__()}.csv"
        mkdir_p(targets_dir)
        targets_fpath = os.path.join(targets_dir, targets_fname)

        info(f"Saving crawl targets to {targets_fpath}")
        with open(targets_fpath, "w") as f:
            f.write("name,cursor,interface\n")
            for target in crawl_targets:
                if target == None:
                    continue
                f.write(f"{target[0]},{target[1]},{target[2]}\n")
        success(f"Saved crawl targets to {targets_fpath}", end=ENDL)

        targets_len = len(crawl_targets)
        for i, target in enumerate(crawl_targets):
            target_name, cursor, _ = target or ("User Root", "/", CanvasCrawlInterfaces.USER)
            info(f"Crawling target {ellipsis(target_name)} and saving to {cursor}")
            try:
                self.crawl(user_id, target)
            except Exception as e:
                error(f"Failed to crawl target {ellipsis(target_name)} and save to {ellipsis(cursor)}")

            info(f"Crawl progress: {i/targets_len*100:.2f}% ({i}/{targets_len})")