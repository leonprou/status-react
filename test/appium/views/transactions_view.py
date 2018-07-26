import time

import pytest
from selenium.common.exceptions import NoSuchElementException
from views.base_element import BaseElement, BaseButton, BaseText
from views.base_view import BaseView


class OptionsButton(BaseButton):
    def __init__(self, driver):
        super(OptionsButton, self).__init__(driver)
        self.locator = self.Locator.xpath_selector(
            '(//android.view.ViewGroup[@content-desc="icon"])[2]')

    class CopyTransactionHashButton(BaseButton):
        def __init__(self, driver):
            super(OptionsButton.CopyTransactionHashButton, self).__init__(driver)
            self.locator = self.Locator.text_selector('Copy transaction hash')

    class OpenOnEtherscanButton(BaseButton):
        def __init__(self, driver):
            super(OptionsButton.OpenOnEtherscanButton, self).__init__(driver)
            self.locator = self.Locator.text_selector('Open on Etherscan.io')


class TransactionTable(BaseElement):
    def __init__(self, driver):
        super(TransactionTable, self).__init__(driver)
        self.driver = driver
        self.locator = self.Locator.xpath_selector("//android.support.v4.view.ViewPager")

    class TransactionElement(BaseButton):
        def __init__(self, driver):
            super(TransactionTable.TransactionElement, self).__init__(driver)

        @staticmethod
        def by_amount(driver, amount: str):
            element = TransactionTable.TransactionElement(driver)
            element.locator = element.Locator.xpath_selector(
                "(//android.widget.TextView[contains(@text,'%s ETH')])" % amount)
            return element

        @staticmethod
        def by_index(driver, index: int):
            element = TransactionTable.TransactionElement(driver)
            element.locator = element.Locator.xpath_selector(
                '(//android.view.ViewGroup[@content-desc="transaction-item"])[%d]' % (index + 1))
            return element

        class TransactionDetailsView(BaseView):
            def __init__(self, driver):
                super(TransactionTable.TransactionElement.TransactionDetailsView, self).__init__(driver)
                self.driver = driver
                self.locators = dict(transaction_hash="//android.widget.TextView[@text='Hash']/following-sibling::*[1]")
                self.options_button = OptionsButton(driver)
                self.copy_transaction_hash_button = OptionsButton.CopyTransactionHashButton(driver)
                self.open_transaction_on_etherscan_button = OptionsButton.OpenOnEtherscanButton(driver)

            class DetailsTextElement(BaseText):
                def __init__(self, driver, locator):
                    super(TransactionTable.TransactionElement.TransactionDetailsView.DetailsTextElement,
                          self).__init__(driver)
                    self.locator = self.Locator.xpath_selector(locator)

            def get_transaction_hash(self) -> str:
                return self.DetailsTextElement(driver=self.driver, locator=self.locators['transaction_hash']).text

        def navigate(self):
            return self.TransactionDetailsView(self.driver)

    def get_first_transaction(self):
        return self.TransactionElement.by_index(self.driver, 0)

    def transaction_by_amount(self, amount: str):
        return self.TransactionElement.by_amount(self.driver, amount=amount.replace(',', '.'))

    def find_transaction(self, amount: str) -> TransactionElement:
        element = self.transaction_by_amount(amount=amount)
        for i in range(9):
            try:
                element.find_element()
                return element
            except NoSuchElementException:
                time.sleep(5)
                self.refresh_transactions()
        pytest.fail('Transaction was not found on Wallet/Transaction screen')

    def refresh_transactions(self):
        self.driver.swipe(500, 500, 500, 1000)


class FiltersButton(BaseButton):
    def __init__(self, driver):
        super(FiltersButton, self).__init__(driver)
        self.locator = self.Locator.accessibility_id('filters-button')


class FilterCheckbox(BaseButton):
    def __init__(self, driver, filter_name):
        super(FilterCheckbox, self).__init__(driver)
        self.locator = self.Locator.xpath_selector(
            "//*[@text='%s']/following-sibling::*[@content-desc='checkbox']" % filter_name)


class TransactionsView(BaseView):
    def __init__(self, driver):
        super(TransactionsView, self).__init__(driver)
        self.driver = driver
        self.filters_button = FiltersButton(self.driver)
        self.transactions_table = TransactionTable(self.driver)

    def filter_checkbox(self, filter_name):
        return FilterCheckbox(self.driver, filter_name)
