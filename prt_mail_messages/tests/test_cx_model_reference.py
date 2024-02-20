###################################################################################
#
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

from .common import MailMessageCommon


class TestCxModelReference(MailMessageCommon):
    """
    TEST 1 : Check 'custom_name' field value
    TEST 2 : Check selection value
    TEST 3 : Check referenceable models list
    """

    def setUp(self):
        super().setUp()

    # -- TEST 1 : Check 'custom_name' field value
    def test_onchange_ir_model_id_record(self):
        """
        Check 'custom_name' field value
        at change 'ir_model_id' field
        """
        expected_value = "Contact"
        self.assertEqual(
            self.cx_model_reference_partner.custom_name,
            expected_value,
            msg=f"Custom name must be equal to '{expected_value}'",
        )

        self.cx_model_reference_partner.onchange_ir_model_id()

        expected_value = self.env.ref("base.model_res_partner").name
        self.assertEqual(
            self.cx_model_reference_partner.custom_name,
            expected_value,
            msg=f"Custom name must be equal to '{expected_value}'",
        )

        self.cx_model_reference_partner.write(
            {"ir_model_id": self.ref("base.model_res_users")}
        )
        self.cx_model_reference_partner.onchange_ir_model_id()

        expected_value = self.env.ref("base.model_res_users").name
        self.assertEqual(
            self.cx_model_reference_partner.custom_name,
            expected_value,
            msg=f"Custom name must be equal to '{expected_value}'",
        )

    # -- TEST 2 : Check selection value
    def test_referenceable_models(self):
        """Check selection value by user"""
        PrtMessageMoveWiz = self.env["prt.message.move.wiz"]

        referable_models_selected = PrtMessageMoveWiz.with_user(
            self.env.user.id
        )._referenceable_models()

        self.assertEqual(
            len(referable_models_selected),
            2,
            msg="Selection item count must be equal to 2",
        )
        res_partner_obj, res_partner_custom_name = referable_models_selected[0]
        (
            cetmix_conversation_obj,
            cetmix_conversation_custom_name,
        ) = referable_models_selected[1]

        self.assertEqual(
            res_partner_obj,
            "res.partner",
            msg="Model name must be equal to 'res.partner'",
        )
        self.assertEqual(
            res_partner_custom_name,
            "Contact",
            msg="Custom name must be equal to 'Contact'",
        )
        self.assertEqual(
            cetmix_conversation_obj,
            "cetmix.conversation",
            msg="Model name must be equal to 'cetmix.conversation'",
        )
        self.assertEqual(
            cetmix_conversation_custom_name,
            "Conversation",
            msg="Custom name must be equal to 'Conversation'",
        )
        referable_models_selected = PrtMessageMoveWiz.with_user(
            self.test_user.id
        )._referenceable_models()

        self.assertEqual(
            len(referable_models_selected),
            1,
            msg="Selection item count must be equal to 1",
        )
        res_partner_obj, res_partner_custom_name = referable_models_selected[0]
        self.assertEqual(
            res_partner_obj,
            "res.partner",
            msg="Model must be equal to 'res.partner'",
        )
        self.assertEqual(
            res_partner_custom_name,
            "Contact",
            msg="Custom name must be equal to 'Contact'",
        )

        self.test_user.write(
            {"groups_id": [(4, self.ref("prt_mail_messages.group_conversation_own"))]}
        )
        referable_models_selected = PrtMessageMoveWiz.with_user(
            self.test_user
        )._referenceable_models()
        self.assertEqual(
            len(referable_models_selected),
            2,
            msg="Selection item count must be equal to 2",
        )
        res_partner_obj, res_partner_custom_name = referable_models_selected[0]
        (
            cetmix_conversation_obj,
            cetmix_conversation_custom_name,
        ) = referable_models_selected[1]

        self.assertEqual(
            res_partner_obj,
            "res.partner",
            msg="Model name must be equal to 'res.partner'",
        )
        self.assertEqual(
            res_partner_custom_name,
            "Contact",
            msg="Custom name must be equal to 'Contact'",
        )
        self.assertEqual(
            cetmix_conversation_obj,
            "cetmix.conversation",
            msg="Model name must be equal to 'cetmix.conversation'",
        )
        self.assertEqual(
            cetmix_conversation_custom_name,
            "Conversation",
            msg="Custom name must be equal to 'Conversation'",
        )

    # -- TEST 3 : Check referenceable models list
    def test_get_referenceable_models_for_user(self):
        """Check referenceable models list"""
        CxModelReference = self.env["cx.model.reference"]

        models_list = CxModelReference.referenceable_models()
        self.assertEqual(len(models_list), 2, msg="Models count must be equal to 2")
        self.assertListEqual(
            list(dict(models_list).keys()),
            ["res.partner", "cetmix.conversation"],
            msg="Models list must be the same",
        )
        models_list = CxModelReference.with_user(self.test_user).referenceable_models()
        self.assertEqual(len(models_list), 1, msg="Models count must be equal to 1")
        self.assertListEqual(
            list(dict(models_list).keys()),
            ["res.partner"],
            msg="Models list must be the same",
        )
        conversation_group_id = self.env.ref(
            "prt_mail_messages.group_conversation_own"
        ).id
        self.test_user.write({"groups_id": [(4, conversation_group_id)]})
        models_list = CxModelReference.referenceable_models()
        self.assertEqual(len(models_list), 2, msg="Models count must be equal to 2")
        self.assertListEqual(
            list(dict(models_list).keys()),
            ["res.partner", "cetmix.conversation"],
            msg="Models list must be the same",
        )
