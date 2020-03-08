from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time

from constants import CUSTOMER_ACCT_NO, TOTAL_AMT, RETRY_LIMIT, SLEEP_TIME
from Payment import Payment

debug = False


class Downloader(object):
    def __init__(self):
        self.raw_text = ""
        self.payments = {}

    def get_payments(self):
        return self.payments

    def retrieve_page_text(self, driver):
        # get text, make sure you got what you expected or else retry until fail.
        correct = False
        tries = 0
        pageText = ""
        while not correct and tries < RETRY_LIMIT:
            pageText = driver.find_element_by_tag_name("body").text
            if CUSTOMER_ACCT_NO in pageText:
                correct = True
            else:
                tries += 1
                if debug:
                    print(tries)
                time.sleep(2 ** tries / 10)

        if CUSTOMER_ACCT_NO not in pageText or TOTAL_AMT not in pageText:
            raise ValueError("Did not find a page with customer details")

        return pageText

    # This method is to open and download the attached report
    def download_report(self, filePath):

        try:
            # open file
            driver = webdriver.Chrome("./chromedriver_mac")
            driver.set_page_load_timeout(30)
            driver.maximize_window()
            driver.get("file://%s" % filePath)

            time.sleep(SLEEP_TIME)

            # open actual text
            driver.find_element_by_id("text_buttonAcknowledge").click()
            time.sleep(SLEEP_TIME)

            self.raw_text = self.retrieve_page_text(driver)
            self.parse_payments_from_raw_text(self.raw_text)
            return self.payments
        except Exception as e:
            print(e)
        finally:
            # remove file when you're done with it
            os.remove(filePath)

    def parse_payments_from_raw_text(self, text):
        # split raw text into array of lines
        lines = text.split("\n")

        # get indices that tell you where to look for payment info
        preceding_index = [
            idx for idx, txt in enumerate(lines) if CUSTOMER_ACCT_NO in txt
        ][0]
        succeeding_index = [idx for idx, txt in enumerate(lines) if TOTAL_AMT in txt][0]
        start_index = preceding_index + 1

        for i in range(start_index, succeeding_index, 2):
            customer_account_no = -1
            last_name = ""
            first_name = ""
            trace_no = -1
            amount = -1
            address = ""

            # chunks will be account no, last name, first name, trace no, amount
            chunks = lines[i].split()
            if len(chunks) != 5:
                raise ValueError(
                    "Expected line to have 5 chunks, got %s instead. Line was %s"
                    % (len(chunks), lines[i])
                )

            # for chunk in chunks:
            #     print(chunks.index(chunk))
            #     print(chunk)

            if chunks[0].isdigit():
                customer_account_no = chunks[0]
            else:
                raise TypeError(
                    "Expected first chunk to be a number. Was %s instead" % chunks[0]
                )

            if not chunks[1].isdigit():
                last_name = chunks[1]
            else:
                raise TypeError(
                    "Expected chunk to be a last name. Was %s instead" % chunks[1]
                )

            if not chunks[2].isdigit():
                first_name = chunks[2]
            else:
                raise TypeError(
                    "Expected chunk to be a first name. Was %s instead" % chunks[2]
                )

            if chunks[3].isdigit():
                trace_no = chunks[3]
            else:
                raise TypeError(
                    "Expected chunk to be a number. Was %s instead" % chunks[3]
                )

            if not chunks[4].isdigit() and chunks[4][0] == "$":
                amount = chunks[4]
            else:
                raise TypeError(
                    "Expected chunk to be a dollar amount. Was %s instead" % chunks[4]
                )

            # add payment
            self.payments[customer_account_no] = Payment(
                customer_account_no, last_name, first_name, trace_no, amount, address
            )
