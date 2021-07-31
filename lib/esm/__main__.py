#!/usr/bin/env python3
import time
import traceback
from urllib.error import URLError

from . import esm_main

if __name__ == '__main__':
    esm_main.init()
    while True:
        try:
            esm_main.main()
        except KeyboardInterrupt:
            break
        except URLError:
            print('[ESM] Cannot connect to comm-NA. Does the server start?')
            time.sleep(1)

        except:
            print('[ESM] ******************')
            print('[ESM] ***   BROKEN   ***')
            print('[ESM] ******************')
            traceback.print_exc()
            time.sleep(1)
            print('[ESM] ******************')
            print('[ESM] *** RESTARTING ***')
            print('[ESM] ******************')
