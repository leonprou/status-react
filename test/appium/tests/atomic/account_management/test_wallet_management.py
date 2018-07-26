import pytest

from tests import marks, transaction_users, camera_access_error_text, common_password
from tests.base_test_case import SingleDeviceTestCase
from views.sign_in_view import SignInView


@marks.all
@marks.account
class TestWalletManagement(SingleDeviceTestCase):

    @marks.testrail_id(3698)
    @marks.smoke_1
    def test_wallet_set_up(self):
        sign_in = SignInView(self.driver)
        sign_in.create_user()
        wallet = sign_in.wallet_button.click()
        text = 'Simple and secure cryptocurrency wallet'
        if not wallet.element_by_text(text).is_element_displayed():
            self.errors.append("'%s' is not displayed" % text)
        wallet.set_up_button.click()
        text = ('This is your personal transaction phrase that you’ll use everytime you make a transaction. '
                'Make sure to write it down on a piece of paper, store it somewhere, '
                'and only confirm transactions when you see these three words.')
        if not wallet.element_by_text(text).is_element_displayed():
            self.errors.append("'%s' text is not displayed" % text)
        phrase_length = len(wallet.sign_in_phrase.list)
        if phrase_length != 3:
            self.errors.append('Transaction phrase length is %s' % phrase_length)
        wallet.done_button.click()
        for text in ['Wrote it down?', 'You won’t be able to see your 3-word transaction phrase again after this.']:
            if not wallet.element_by_text(text).is_element_displayed():
                self.errors.append("'%s' text is not displayed" % text)
        wallet.yes_button.click()
        for element in [wallet.send_transaction_button, wallet.receive_transaction_button,
                        wallet.transaction_history_button]:
            if not element.is_element_displayed():
                self.errors.append('%s button is not shown after wallet setup' % element.name)
        self.verify_no_errors()

    @marks.testrail_id(1449)
    def test_open_transaction_on_etherscan(self):
        user = transaction_users['A_USER']
        sign_in_view = SignInView(self.driver)
        home_view = sign_in_view.recover_access(user['passphrase'], user['password'])
        wallet_view = home_view.wallet_button.click()
        wallet_view.set_up_wallet()
        transactions_view = wallet_view.transaction_history_button.click()
        transaction_details = transactions_view.transactions_table.get_first_transaction().click()
        transaction_hash = transaction_details.get_transaction_hash()
        transaction_details.options_button.click()
        transaction_details.open_transaction_on_etherscan_button.click()
        base_web_view = wallet_view.get_base_web_view()
        base_web_view.open_in_webview()
        base_web_view.find_text_part(transaction_hash)

    @marks.testrail_id(1450)
    def test_copy_transaction_hash(self):
        user = transaction_users['A_USER']
        sign_in_view = SignInView(self.driver)
        home_view = sign_in_view.recover_access(user['passphrase'], user['password'])
        wallet_view = home_view.wallet_button.click()
        wallet_view.set_up_wallet()
        transactions_view = wallet_view.transaction_history_button.click()
        transaction_details = transactions_view.transactions_table.get_first_transaction().click()
        transaction_hash = transaction_details.get_transaction_hash()
        transaction_details.options_button.click()
        transaction_details.copy_transaction_hash_button.click()
        transaction_details.get_back_to_home_view()
        wallet_view.home_button.click()
        public_chat = home_view.join_public_chat('testchat')
        public_chat.chat_message_input.paste_text_from_clipboard()
        if public_chat.chat_message_input.text != transaction_hash:
            pytest.fail('Transaction hash was not copied')

    @marks.testrail_id(3713)
    @marks.smoke_1
    def test_manage_assets(self):
        sign_in = SignInView(self.driver)
        sign_in.create_user()
        wallet = sign_in.wallet_button.click()
        wallet.set_up_wallet()
        wallet.options_button.click()
        wallet.manage_assets_button.click()
        select_asset = 'MDS'
        deselect_asset = 'STT'
        wallet.asset_checkbox_by_name(select_asset).click()
        wallet.asset_checkbox_by_name(deselect_asset).click()
        wallet.done_button.click()
        if not wallet.asset_by_name(select_asset).is_element_displayed():
            self.errors.append('%s asset is not shown in wallet' % select_asset)
        if wallet.asset_by_name(deselect_asset).is_element_displayed():
            self.errors.append('%s asset is shown in wallet but was deselected' % deselect_asset)
        self.verify_no_errors()

    @marks.testrail_id(3725)
    def test_backup_recovery_phrase_warning_from_wallet(self):
        sign_in = SignInView(self.driver)
        sign_in.create_user()
        wallet = sign_in.wallet_button.click()
        wallet.set_up_wallet()
        if wallet.backup_recovery_phrase.is_element_present():
            pytest.fail("'Backup your Recovery phrase' option is shown on Wallet for an account with no funds")
        wallet.receive_transaction_button.click()
        address = wallet.address_text.text[2:]
        wallet.get_back_to_home_view()
        home = wallet.home_button.click()
        self.network_api.get_donate(address)
        home.wallet_button.click()
        if not wallet.backup_recovery_phrase.is_element_present():
            pytest.fail("'Backup your Recovery phrase' option is not shown on Wallet for an account with funds")
        profile = wallet.get_profile_view()
        profile.backup_recovery_phrase()

    @marks.testrail_id(3777)
    def test_no_collectibles_to_send_from_wallet(self):
        sign_in = SignInView(self.driver)
        sign_in.create_user()
        profile = sign_in.profile_button.click()
        profile.switch_network('Mainnet with upstream RPC')
        sign_in.sign_in()
        wallet = sign_in.wallet_button.click()
        wallet.set_up_wallet()
        wallet.options_button.click()
        wallet.manage_assets_button.click()
        asset_name = 'CryptoKitties'
        wallet.asset_checkbox_by_name(asset_name).click()
        wallet.done_button.click()
        send_transaction = wallet.send_transaction_button.click()
        send_transaction.select_asset_button.click()
        if send_transaction.asset_by_name(asset_name).is_element_displayed():
            pytest.fail('Collectibles can be sent from wallet')

    @marks.testrail_id(2176)
    def test_deny_camera_access_scanning_wallet_adders(self):
        sign_in = SignInView(self.driver)
        sign_in.create_user()
        wallet = sign_in.wallet_button.click()
        wallet.set_up_wallet()
        send_transaction = wallet.send_transaction_button.click()
        send_transaction.chose_recipient_button.click()
        send_transaction.scan_qr_code_button.click()
        send_transaction.deny_button.click()
        send_transaction.element_by_text(camera_access_error_text).wait_for_visibility_of_element(3)
        send_transaction.ok_button.click()
        send_transaction.chose_recipient_button.click()
        send_transaction.scan_qr_code_button.click()
        send_transaction.deny_button.wait_for_visibility_of_element(2)

    @marks.testrail_id(3730)
    def test_filter_transactions_history(self):
        sign_in_view = SignInView(self.driver)
        sign_in_view.create_user()
        wallet_view = sign_in_view.wallet_button.click()
        wallet_view.set_up_wallet()
        address = wallet_view.get_wallet_address()

        # get incoming transaction
        self.network_api.get_donate(address=address)

        # get outgoing transaction
        send_transaction = wallet_view.send_transaction_button.click()
        send_transaction.amount_edit_box.click()
        send_amount = send_transaction.get_unique_amount()
        send_transaction.amount_edit_box.set_value(send_amount)
        send_transaction.confirm()
        send_transaction.chose_recipient_button.click()
        send_transaction.enter_recipient_address_button.click()
        send_transaction.enter_recipient_address_input.set_value(transaction_users['C_USER']['address'])
        send_transaction.done_button.click()
        send_transaction.sign_transaction(common_password)

        # filtering
        transaction_history = wallet_view.transaction_history_button.click()
        transaction_history.filters_button.click()
        for filter_name in 'Outgoing', 'Pending', 'Failed':
            transaction_history.filter_checkbox(filter_name).click()
        wallet_view.done_button.click()
        incoming_transaction = transaction_history.transactions_table.transaction_by_amount('0.1')
        outgoing_transaction = transaction_history.transactions_table.transaction_by_amount(send_amount)
        if not incoming_transaction.is_element_displayed():
            self.errors.append('Incoming transaction is not shown after selecting incoming filter')
        if outgoing_transaction.is_element_displayed():
            self.errors.append('Outgoing transaction is shown after selecting incoming filter')

        transaction_history.filters_button.click()
        for filter_name in 'Outgoing', 'Incoming':
            transaction_history.filter_checkbox(filter_name).click()
        wallet_view.done_button.click()
        if not outgoing_transaction.is_element_displayed():
            self.errors.append('Outgoing transaction is not shown after selecting outgoing filter')
        if incoming_transaction.is_element_displayed():
            self.errors.append('Incoming transaction is shown after selecting outgoing filter')
        self.verify_no_errors()
