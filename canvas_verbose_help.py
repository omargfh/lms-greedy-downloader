from console import cfmt
canvas_verbose_help_message = f"""
Canvas Greedy Downloader
========================
This script downloads all files for a given user from Canvas.
It is a greedy downloader, meaning it will download all files
available to the user, including hidden files. This script
will create a folder structure that mirrors the Canvas file
system. This script depends on the Chrome WebDriver and cURL
binary. The Chrome WebDriver must be installed and in your
PATH. The cURL binary must be installed and in your PATH.
If they are not, you can override them using the provided
.env file or command line arguments.

Usage
-----
$ python canvas-greedy-downloader.py [-h] [-user_id USER_ID] [-domain DOMAIN] [-output OUTPUT]
                  [-chrome_profile_path CHROME_PROFILE_PATH]
                  [-chrome_profile_name CHROME_PROFILE_NAME]
                  [-chrome_binary_path CHROME_BINARY_PATH] [-curl_path CURL_PATH] [-skip-tests]
                  [-skip-login] [-skip-download] [-include-user-root] [-include-courses]
                  [-include-groups] [-include-modules] [-include-all] [-output-fs-tree]
                  [-store-cookies] [-use-threads] [-courses COURSES] [-v] [-H]

Options
-------
  -h, --help            show this help message and exit
  -user_id USER_ID      Canvas user ID
  -domain DOMAIN        Canvas domain
  -output OUTPUT        Output directory
  -chrome_profile_path CHROME_PROFILE_PATH
                        Chrome profile path
  -chrome_profile_name CHROME_PROFILE_NAME
                        Chrome profile path
  -chrome_binary_path CHROME_BINARY_PATH
                        Chrome binary path
  -curl_path CURL_PATH  cURL path
  -skip-tests           Skip running tests
  -skip-login           Skip the login step
  -skip-download        Skip downloading files
  -include-user-root    Include the user's root folder in the output directory
  -include-courses      Include course folders in the output directory
  -include-groups       Include module folders in the output directory
  -include-modules      Include module folders in the output directory
  -include-all          Override all include flags
  -output-fs-tree       Output the file system tree to the console
  -store-cookies        Store cookies for future use
  -use-threads          Use threads to download files
  -courses COURSES      Comma separated list of course prefixes to download
  -v, --version         show program's version number and exit
  -H, --verbose-help    Show the verbose help message

Environment Variables
---------------------
Each option can be set to have a default value in the .env file or using the shell's environment.

The following environment variables can be set:
  - CANVAS_USER_ID: Canvas user ID
  - CANVAS_DOMAIN: Canvas domain
  - OUTPUT_DIR: Output directory
  - CHROME_PROFILE_PATH: Chrome profile path
  - CHROME_PROFILE_NAME: Chrome profile name
  - CHROME_BINARY_PATH: Chrome binary path
  - CURL_PATH: cURL path
  - SKIP_TESTS: Skip running tests
  - SKIP_LOGIN: Skip the login step
  - SKIP_DOWNLOAD: Skip downloading files
  - INCLUDE_USER_ROOT_FOLDER: Include the user's root folder in the output directory
  - INCLUDE_COURSE_FOLDERS: Include course folders in the output directory
  - INCLUDE_GROUP_FOLDERS: Include module folders in the output directory
  - INCLUDE_MODULE_FOLDERS: Include module folders in the output directory
  - OUTPUT_FS_TREE: Output the file system tree to the console
  - STORE_COOKIES: Store cookies for future use
  - COURSES: Comma separated list of course prefixes or IDs to download (e.g. BIOS, BUSN 201, BUSN 2, 1562217)
  - USE_THREADS: Use threads to download files (default: False) [threads are only used for cURL downloads]

Examples
--------

* Download all files for user 12345 from mylms.instructure.com to the current directory:
{cfmt("$ python canvas-greedy-downloader.py -user_id 12345 -domain mylms.instructure.com -include-all", "success", "info")}

* Download all files for user 12345 from mylms.instructure.com to the /tmp directory:
{cfmt("$ python canvas-greedy-downloader.py -user_id 12345 -domain mylms.instructure.com -output /tmp -include-all", "success", "info")}

* Download all courses starting with "BIOS" for user 12345 from mylms.instructure.com to the current directory:
{cfmt("$ python canvas-greedy-downloader.py -user_id 12345 -domain mylms.instructure.com -courses BIOS -include-courses", "success", "info")}

Download all BIOS courses, all level 200 BUSN courses, and course 1562217 for user 12345 from mylms.instructure.com to the * current directory:
{cfmt("$ python canvas-greedy-downloader.py -user_id 12345 -domain mylms.instructure.com -courses \"BIOS, BUSN 2, 1562217\" -include-courses -include-groups -include-modules", "success", "info")}

* Use a custom Chrome profile:
{cfmt('$ python canvas-greedy-downloader.py -user_id 12345 -domain mylms.instructure.com -include-all -chrome_profile_path /path/to/profile -chrome_profile_name "Profile 1"', "success", "info")}

* Use a custom Chrome driver:
{cfmt('$ python canvas-greedy-downloader.py -user_id 12345 -domain mylms.instructure.com -include-all -chrome_binary_path /path/to/chrome', "success", "info")}
"""


test_help_messages = {
    "driver.startup": "This test checks if the Chrome WebDriver can be started. If this test fails, check if the Chrome WebDriver is installed and in your PATH (or your CHROME_BINARY_PATH environment variable is correctly set). Also, check if selenium and webdriver-manager are installed correctly in your Python environment.",
    "driver.canDownload": "This test checks if Chrome can download a file using the built-in .download_file() method. Expect this test to fail. We use a workaround that uses cURL.",
    "cURL.canDownload": "This test checks if cURL can download a file. If this test fails, check if cURL is installed and in your PATH (or your CURL_PATH environment variable is correctly set). Also, check if you have the correct permissions to write to the output directory.",
}

instructions = {
    "lms.login": "You will be prompted to log in to your Canvas account. You must log in to continue. If you are already logged in, you can skip this step. If your Chrome settings keep your profile logged in, you may pass the --skip-login flag to skip this step.",
    "lms.skipLogin": "You have passed the --skip-login flag. The script will not attempt to log in to your Canvas account. If you are not already logged in, the script will fail. If you passed the -store-cookies flag and a cookies.pkl file exists, the script will attempt to load the cookies from the file.",
}