- nostr-watch.py
    - This script monitors the nostr.watch website and checks the availability of relays using the nostr.watch API.
- crawl.py
    - This script includes the crawl_relay function, which retrieves events from the relay and saves them to a file.
- gen_jobs.py
    - This script generates a list of jobs that can be passed to the crawl_relay function.

---

The workflow involves:
1. Using nostr-watch.py to retrieve and maintain a list of relays from nostr.watch.
2. Generating jobs for the relays using gen_jobs.py.
3. Passing the generated jobs to the crawl_relay function.

As my script used for this process was very ad hoc and was created for an ad hoc environment, it is not included here.

---

Additionally, please note that the script relies on the pynostr library, which has been updated to accommodate new relay features. You may need to make slight modifications to the code if necessary.