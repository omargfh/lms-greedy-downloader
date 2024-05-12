import argparse as ap
import time
import os
import sys
import copy

from console import error, info, cprint, bprint
from test import it, TestKit

from canvas_figlet import canvas_greedy_downloader_figlet
from canvas_verbose_help import canvas_verbose_help_message, test_help_messages, instructions
from canvas_selenium import get_driver, login, save_cookie, load_cookie, get_executable_path
from canvas_dataclasses import CrawlerConfig, CanvasCrawlOptions
from canvas_filesystem_crawl import CanvasFileSystemCrawl
from constants import SEP, ENDL

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC


from dotenv import load_dotenv
load_dotenv()

# Version
VERSION = "1.0.0"

# Lambda functions
default_value = lambda env_name : os.getenv(env_name).lower() == "true"

# usage: python3 canvas-greedy-downloader.py -user_id [id] -domain [domain] -output [output_directory]
argp = ap.ArgumentParser()
argp.add_argument("-user_id", type=int, help="Canvas user ID", default=int(os.getenv("CANVAS_USER_ID")) )
argp.add_argument("-domain", type=str, help="Canvas domain", default=os.getenv("CANVAS_DOMAIN"))
argp.add_argument("-output", type=str, help="Output directory", default=os.getenv("OUTPUT_DIR"))
argp.add_argument("-chrome_profile_path", type=str, help="Chrome profile path", default=os.getenv("CHROME_PROFILE_PATH"))
argp.add_argument("-chrome_profile_name", type=str, help="Chrome profile path", default=os.getenv("CHROME_PROFILE_NAME"))
argp.add_argument("-chrome_binary_path", type=str, help="Chrome binary path", default=os.getenv("CHROME_BINARY_PATH"))
argp.add_argument("-curl_path", type=str, help="cURL path", default=os.getenv("CURL_PATH"))
argp.add_argument("-skip-tests", action="store_true", help="Skip running tests", default=os.getenv("SKIP_TESTS").lower() == "true")
argp.add_argument("-skip-login", action="store_true", help="Skip the login step", default=os.getenv("SKIP_LOGIN").lower() == "true")
argp.add_argument("-skip-download", action="store_true", help="Skip downloading files", default=os.getenv("SKIP_DOWNLOAD").lower() == "true")
argp.add_argument("-include-user-root", action="store_true", help="Include the user's root folder in the output directory", default=default_value("INCLUDE_USER_ROOT_FOLDER"))
argp.add_argument("-include-courses", action="store_true", help="Include course folders in the output directory", default=default_value("INCLUDE_COURSE_FOLDERS"))
argp.add_argument("-include-groups", action="store_true", help="Include module folders in the output directory", default=default_value("INCLUDE_MODULE_FOLDERS"))
argp.add_argument("-include-modules", action="store_true", help="Include module folders in the output directory", default=default_value("INCLUDE_MODULE_FOLDERS"))
argp.add_argument("-include-all", action="store_true", help="Override all include flags", default=False)
argp.add_argument("-output-fs-tree", action="store_true", help="Output the file system tree to the console", default=default_value("OUTPUT_FS_TREE"))
argp.add_argument("-store-cookies", action="store_true", help="Store cookies for future use", default=default_value("STORE_COOKIES"))
argp.add_argument("-use-threads", action="store_true", help="Use threads to download files", default=default_value("USE_THREADS"))
argp.add_argument("-courses", type=str, help="Comma separated list of course prefixes to download", default=None)
argp.add_argument("-v", "--version", action="version", version=VERSION)
argp.add_argument("-H", "--verbose-help", action="store_true", help="Show the verbose help message")

args = argp.parse_args()
args = {k: v if v != "" else None for k, v in dict(args._get_kwargs()).items()}

courses = [x.strip() for x in args["courses"].split(",")] if args["courses"] is not None else None

# Show help message
if args['verbose_help']:
    cprint(canvas_verbose_help_message, "info")
    sys.exit(0)

# Validation: include-all
includes = ["include_user_root", "include_courses", "include_groups", "include_modules"]
if args["include_all"]:
    for i in includes:
        args[i] = True

# Validation: required
required = {"user_id", "domain"}
for k,v in args.items():
    if (v is None) and (k in required):
        error(f"XXX - Missing required argument {k}")
        sys.exit(1)

# Validation: overrides
overrides = {"curl_path": "curl", "output": "."}
for k,v in overrides.items():
    if (args[k] is None):
        args[k] = v

# Final values
USER_ID = args["user_id"]
CANVAS_DOMAIN = args["domain"]
OUTPUT_DIR = args["output"]
CHROME_PROFILE_PATH = args["chrome_profile_path"]
CHROME_PROFILE_NAME = args["chrome_profile_name"]
CHROME_BINARY_PATH = args["chrome_binary_path"]
CURL_PATH = args["curl_path"]

# Print the system runtime configuration
cprint(canvas_greedy_downloader_figlet, "info")

cprint(f"\t * Canvas user ID: {USER_ID}", "info")
cprint(f"\t * Canvas domain: {CANVAS_DOMAIN}", "info")
cprint(f"\t * Output directory: {OUTPUT_DIR}", "info")
cprint(f"\t * Chrome profile path: {CHROME_PROFILE_PATH}", "info")
cprint(f"\t * Chrome profile name: {CHROME_PROFILE_NAME}", "info")
cprint(f"\t * Chrome binary path: {"Default" if not CHROME_BINARY_PATH else CHROME_BINARY_PATH}", "info")
cprint(f"\t * Chrome driver path: {get_executable_path()}", "info")
cprint(f"\t * cURL path: {CURL_PATH}", "info")
cprint(f"\t * Skip tests: ", "info", end=""); bprint(args["skip_tests"])
cprint(f"\t * Skip login: ", "info", end=""); bprint(args["skip_login"])
cprint(f"\t * Skip download: ", "info", end=""); bprint(args["skip_download"])
cprint(f"\t * Include user root folder: ", "info", end=""); bprint(args["include_user_root"])
cprint(f"\t * Include course folders: ", "info", end=""); bprint(args["include_courses"])
cprint(f"\t * Include group folders: ", "info", end=""); bprint(args["include_groups"])
cprint(f"\t * Include module folders: ", "info", end=""); bprint(args["include_modules"])
cprint(f"\t * Include all: ", "info", end=""); bprint(args["include_all"])
cprint(f"\t * Output file system tree: ", "info", end=""); bprint(args["output_fs_tree"]);
cprint(f"\t * Store cookies: ", "info", end=""); bprint(args["store_cookies"])
cprint(f"\t * Use threads: ", "info", end=""); bprint(args["use_threads"])
cprint(f"\t * Courses: {courses if courses is not None else "No subset selected. Crawls all."}", "info")
cprint(f"\t * Version: {VERSION}", "info")
print(SEP)

input("Press Enter to continue...")
print(SEP)


# Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir={}".format(CHROME_PROFILE_PATH))
chrome_options.add_argument("--enable-managed-downloads")
chrome_options.add_argument("--no-sandbox")

if CHROME_PROFILE_NAME is not None:
    chrome_options.add_argument(f"profile-directory={CHROME_PROFILE_NAME}")
chrome_options.enable_downloads = True

chrome_options.add_experimental_option("prefs", {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing_for_trusted_sources_enabled": False,
    "safebrowsing.enabled": False,
    "credentials_enable_service": True,
    "profile.password_manager_enabled": True
})

# Running tests
if args["skip_tests"] is False:
    tk = TestKit()

    @it("Driver Startup", tk, help=test_help_messages["driver.startup"])
    def test_driver_startup():
        driver = get_driver(chrome_options, CHROME_BINARY_PATH)
        assert driver is not None
        driver.quit()

    @it("Driver can download file", tk, optional=True, help=test_help_messages["driver.canDownload"])
    def test_driver_download_file():
        driver = get_driver(chrome_options, CHROME_BINARY_PATH)
        driver.download_file("https://mp4-download.com/4k-MP4", "test.mp4")
        os.remove("test.mp4")
        driver.quit()

    @it("cURL can download file", tk, help=test_help_messages["cURL.canDownload"])
    def test_curl_download_file():
        os.system(f"{CURL_PATH} -o test.mp4 https://mp4-download.com/4k-MP4")
        os.remove("test.mp4")

    cprint("Running tests...", "info")

    test_driver_startup()
    test_driver_download_file()
    test_curl_download_file()

    tk.done()

    print(ENDL)

driver = get_driver(chrome_options, CHROME_BINARY_PATH)
if not args["skip_login"]:
    cprint(f"{instructions['lms.login']}", "info")
    login(driver, f"https://{CANVAS_DOMAIN}/login")
    driver.get(f"https://{CANVAS_DOMAIN}")
    args["store_cookies"] and save_cookie(driver, "cookies.pkl")
elif args["store_cookies"]:
    cprint(f"{instructions['lms.skipLogin']}", "info")
    driver.get(f"https://{CANVAS_DOMAIN}")
    try:
        load_cookie(driver, "cookies.pkl")
    except Exception as e:
        error(f"Failed to load cookies")
        info(f"Will prompt for login...")
        login(driver, f"https://{CANVAS_DOMAIN}/login")

config = CrawlerConfig(
    user_id=USER_ID,
    canvas_domain=CANVAS_DOMAIN,
    output=OUTPUT_DIR,
    curl_path=CURL_PATH,
    skip_download=args["skip_download"],
    use_threads=args["use_threads"]
)
crawler = CanvasFileSystemCrawl(driver, config)

start = time.time()
options = CanvasCrawlOptions(
    include_user_root_target=args["include_user_root"],
    include_courses=args["include_courses"],
    include_groups=args["include_groups"],
    include_modules=args["include_modules"],
    courses=courses
)
crawler.crawl_all(USER_ID, options)
end = time.time()

cprint(f"Time elapsed: {(end-start)/60:.2f} minutes", "info")