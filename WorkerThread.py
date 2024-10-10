import threading
from ItemScraping import GoogleImagesScraping
from ItemStorage import DataWithException

class WorkerThread(threading.Thread):
    lock_file_exceptions = threading.Lock()
    lock_selenium_grid = threading.Lock()
    
    def __init__(self, thread_id, shared_list=None, proxyLoader=None, with_selenium_grid= True):
        
        super(WorkerThread, self).__init__()
        
        self.thread_id = thread_id
        self.shared_list = shared_list
        self.proxyLoader = proxyLoader
        self.with_selenium_grid = with_selenium_grid
        
        self.proxy = None
        self.PROXY_HOST = None # rotating proxy or host
        self.PROXY_PORT =  None # port
        self.PROXY_USER = None # username
        self.PROXY_PASS = None # password
        
        self.item = None

    def run(self):
        with self.proxyLoader.lock:
            self.proxy = self.proxyLoader.get_proxy(29 - self.thread_id)
        # self.init_proxy()

        self.googleImagesScraping = GoogleImagesScraping(PROXY_HOST=self.PROXY_HOST, PROXY_PORT=self.PROXY_PORT, PROXY_USER=self.PROXY_USER,
                                                    PROXY_PASS=self.PROXY_PASS, workerThread=self, with_selenium_grid=self.with_selenium_grid)
        self.googleImagesScraping.move_to_images_page()
        
        while True:
            try:
                # Access the shared list synchronously
                with self.shared_list.lock:
                    if not self.shared_list.data:
                        break  # The list is empty, the thread ends
                    self.item = self.shared_list.data.pop(0)
                
                # print(f"*"*100)
                # print(f"start = {self.item} ||| by_thread_id = {self.thread_id}")
                # print(f"*"*100)
                    
                self.start_scraping()

            except Exception as e:
                print(e)
                self.googleImagesScraping = GoogleImagesScraping(PROXY_HOST=self.PROXY_HOST, PROXY_PORT=self.PROXY_PORT, PROXY_USER=self.PROXY_USER,
                                                    PROXY_PASS=self.PROXY_PASS, workerThread=self, with_selenium_grid=self.with_selenium_grid)
                self.googleImagesScraping.move_to_images_page()
                
                with WorkerThread.lock_file_exceptions :
                    DataWithException(value = self.item)
        self.googleImagesScraping.driver.quit()
        
    def init_proxy(self):
        self.PROXY_HOST = self.proxy["PROXY_HOST"] # rotating proxy or host
        self.PROXY_PORT = self.proxy["PROXY_PORT"] # port
        self.PROXY_USER = self.proxy["PROXY_USER"] # username
        self.PROXY_PASS = self.proxy["PROXY_PASS"] # password
        
    def start_scraping(self):
        self.googleImagesScraping.get_images_with_key_words(self.item)