from .framework import (
    selenium_test,
    SeleniumTestCase
)


class CollectionBuildersTestCase(SeleniumTestCase):

    ensure_registered = True

    @selenium_test
    def test_build_list_simple_hidden(self):
        self.perform_upload(self.get_filename("1.fasta"))
        self.history_panel_wait_for_hid_ok(1)
        self.history_panel_multi_operations_show()
        self.history_panel_muli_operation_select_hid(1)
        self.history_panel_multi_operation_action_click(self.navigation.history_panel.multi_operations.labels.build_list)

        self.collection_builder_set_name("my cool list")
        self.screenshot("collection_builder_list")
        self.collection_builder_create()
        self._collection_builder_wait_for_hid_ok(2)

    @selenium_test
    def test_build_list_and_show_items(self):
        self.perform_upload(self.get_filename("1.fasta"))
        self.history_panel_wait_for_hid_ok(1)
        self.history_panel_multi_operations_show()
        self.history_panel_muli_operation_select_hid(1)
        self.history_panel_multi_operation_action_click(self.navigation.history_panel.multi_operations.labels.build_list)

        # this toggles the checkbox to not hide originals
        self.collection_builder_hide_originals()
        self.collection_builder_set_name("my cool list")

        self.collection_builder_create()
        self._collection_builder_wait_for_hid_ok(3)

    @selenium_test
    def test_build_pair_simple_hidden(self):
        self.perform_upload(self.get_filename("1.tabular"))
        self.perform_upload(self.get_filename("2.tabular"))
        self._wait_for_hid_visible(1)
        self._wait_for_hid_visible(2)
        self.history_panel_multi_operations_show()
        self.history_panel_muli_operation_select_hid(1)
        self.history_panel_muli_operation_select_hid(2)
        self.history_panel_multi_operation_action_click(self.navigation.history_panel.multi_operations.labels.build_pair)
        self.collection_builder_set_name("my awesome pair")
        self.screenshot("collection_builder_pair")
        self.collection_builder_create()
        self._collection_builder_wait_for_hid_ok(3)

    def _collection_builder_wait_for_hid_ok(self, hid):
        # a hacked up version of super().history_panel_wait_for_hid_ok for beta history panel not refreshing correctly.
        allowed_force_refreshes = 0
        if self.use_beta_history:
            # so collection builder no longer forces refreshes of history panel.
            # Why doesn't the panel pick it up automatically - an sqlite limitation?
            # Or maybe refresh doesn't work if things are selected in the panel?
            allowed_force_refreshes = 2
        self.history_panel_wait_for_hid_ok(hid, allowed_force_refreshes=allowed_force_refreshes)

    @selenium_test
    def test_build_paired_list_simple(self):
        self.perform_upload(self.get_filename("1.tabular"))
        self.perform_upload(self.get_filename("2.tabular"))
        self._wait_for_hid_visible(1)
        self._wait_for_hid_visible(2)
        self.history_panel_multi_operations_show()
        self.history_panel_muli_operation_select_hid(1)
        self.history_panel_muli_operation_select_hid(2)
        self.history_panel_multi_operation_action_click(self.navigation.history_panel.multi_operations.labels.build_list_pairs)

        self.collection_builder_clear_filters()
        self.collection_builder_click_paired_item("forward", 0)
        self.collection_builder_click_paired_item("reverse", 1)
        self.collection_builder_set_name("my awesome paired list")
        self.screenshot("collection_builder_paired_list")
        self.collection_builder_create()
        self._collection_builder_wait_for_hid_ok(3)
        self.history_panel_wait_for_hid_hidden(1)
        self.history_panel_wait_for_hid_hidden(2)

    @selenium_test
    def test_build_paired_list_show_original(self):
        self.perform_upload(self.get_filename("1.tabular"))
        self.perform_upload(self.get_filename("2.tabular"))
        self._wait_for_hid_visible(1)
        self._wait_for_hid_visible(2)
        self.history_panel_multi_operations_show()
        self.history_panel_muli_operation_select_hid(1)
        self.history_panel_muli_operation_select_hid(2)
        self.history_panel_multi_operation_action_click(self.navigation.history_panel.multi_operations.labels.build_list_pairs)

        self.wait_for_and_click(self.navigation.collection_builders.selectors.clear_filters)

        forward_column = self.wait_for_visible(self.navigation.collection_builders.selectors.forward_datasets)
        first_datset_forward = forward_column.find_elements_by_css_selector("li")[0]
        first_datset_forward.click()

        reverse_column = self.wait_for_visible(self.navigation.collection_builders.selectors.reverse_datasets)
        second_dataset_reverse = reverse_column.find_elements_by_css_selector("li")[1]
        second_dataset_reverse.click()

        # this toggles the checkbox to not hide originals
        self.collection_builder_hide_originals()
        self.collection_builder_set_name("my awesome paired list")

        self.collection_builder_create()
        self._collection_builder_wait_for_hid_ok(5)
        self.history_panel_refresh_click()
        self.history_panel_wait_for_hid_ok(1)
        self.history_panel_wait_for_hid_ok(2)
        self.history_panel_wait_for_hid_hidden(3)
        self.history_panel_wait_for_hid_hidden(4)

    @selenium_test
    def test_build_simple_list_via_rules_hidden(self):
        self.perform_upload(self.get_filename("1.fasta"))
        self.history_panel_wait_for_hid_ok(1, allowed_force_refreshes=1)
        self.history_panel_multi_operations_show()
        self.history_panel_muli_operation_select_hid(1)
        self.history_panel_multi_operation_action_click(self.navigation.history_panel.multi_operations.labels.build_from_rules)

        self.collection_builder_set_name("my cool list")
        self.screenshot("collection_builder_rules_list")
        self.collection_builder_create()
        self.history_panel_wait_for_hid_ok(2, allowed_force_refreshes=1)
        self.history_panel_wait_for_hid_hidden(1)

    def _wait_for_hid_visible(self, hid):
        self.history_panel_wait_for_hid_visible(hid, allowed_force_refreshes=1)
