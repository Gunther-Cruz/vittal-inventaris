import unittest

from app import create_app
from app.domain.enums import OperationalStatus
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.usuario_service import UsuarioService


class AssetAllocationServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.inventory_service = InventoryService()
        self.usuario_service = UsuarioService()
        self.technician = self.usuario_service.cadastrar_usuario(
            {
                "nome": "Tecnico IFRS",
                "email": "tecnico@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "TECNICO",
            }
        )
        self.laboratory = self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )
        self.workstation = self.inventory_service.create_workstation(
            self.laboratory,
            {"code": "E01", "map_position_x": "", "map_position_y": "", "notes": ""},
        )
        self.other_workstation = self.inventory_service.create_workstation(
            self.laboratory,
            {"code": "E02", "map_position_x": "", "map_position_y": "", "notes": ""},
        )
        self.computer_case = self.inventory_service.create_computer_case(self._computer_case_data())
        self.monitor = self.inventory_service.create_monitor(self._monitor_data())

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_assign_computer_case_sets_current_binding_and_status(self):
        allocation = self.inventory_service.assign_computer_case_to_workstation(
            self.computer_case,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        self.assertIsNotNone(allocation.id)
        self.assertIsNone(allocation.end_at)
        self.assertEqual(self.computer_case.id, self.workstation.current_computer_case_id)
        self.assertEqual(OperationalStatus.EM_FUNCIONAMENTO, self.computer_case.operational_status)

    def test_unassign_computer_case_closes_history_and_changes_status(self):
        self.inventory_service.assign_computer_case_to_workstation(
            self.computer_case,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        allocation = self.inventory_service.unassign_computer_case_from_workstation(
            self.workstation,
            self.technician,
            {
                "movement_reason": "Removed for technical assessment",
                "operational_status": "EM_MANUTENCAO",
            },
        )

        self.assertIsNotNone(allocation.end_at)
        self.assertIsNone(self.workstation.current_computer_case_id)
        self.assertEqual(OperationalStatus.EM_MANUTENCAO, self.computer_case.operational_status)

    def test_assign_monitor_sets_current_binding_and_status(self):
        allocation = self.inventory_service.assign_monitor_to_workstation(
            self.monitor,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        self.assertIsNotNone(allocation.id)
        self.assertEqual(self.monitor.id, self.workstation.current_monitor_id)
        self.assertEqual(OperationalStatus.EM_FUNCIONAMENTO, self.monitor.operational_status)

    def test_unassign_monitor_to_functional_unassigned(self):
        self.inventory_service.assign_monitor_to_workstation(
            self.monitor,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        self.inventory_service.unassign_monitor_from_workstation(
            self.workstation,
            self.technician,
            {"movement_reason": "Reserve monitor", "operational_status": "FUNCIONAL_DESALOCADO"},
        )

        self.assertIsNone(self.workstation.current_monitor_id)
        self.assertEqual(OperationalStatus.FUNCIONAL_DESALOCADO, self.monitor.operational_status)

    def test_rejects_assignment_when_workstation_already_has_computer_case(self):
        other_case = self.inventory_service.create_computer_case(
            self._computer_case_data(asset_tag="PAT-002", serial_number="SN-002")
        )
        self.inventory_service.assign_computer_case_to_workstation(
            self.computer_case,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        with self.assertRaisesRegex(ValueError, "Workstation already has a computer case."):
            self.inventory_service.assign_computer_case_to_workstation(
                other_case,
                self.workstation,
                self.technician,
                {"movement_reason": "Should fail"},
            )

    def test_rejects_assignment_when_asset_has_active_allocation(self):
        self.inventory_service.assign_computer_case_to_workstation(
            self.computer_case,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        with self.assertRaisesRegex(ValueError, "Only unassigned functional computer cases can be assigned."):
            self.inventory_service.assign_computer_case_to_workstation(
                self.computer_case,
                self.other_workstation,
                self.technician,
                {"movement_reason": "Should fail"},
            )

    def test_rejects_assignment_of_asset_not_functional_unassigned(self):
        self.inventory_service.set_computer_case_status(self.computer_case, "EM_MANUTENCAO")

        with self.assertRaisesRegex(ValueError, "Only unassigned functional computer cases can be assigned."):
            self.inventory_service.assign_computer_case_to_workstation(
                self.computer_case,
                self.workstation,
                self.technician,
                {"movement_reason": "Should fail"},
            )

    def test_rejects_direct_status_change_for_assigned_computer_case(self):
        self.inventory_service.assign_computer_case_to_workstation(
            self.computer_case,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        with self.assertRaisesRegex(ValueError, "Assigned assets must have their status changed"):
            self.inventory_service.set_computer_case_status(self.computer_case, "EM_MANUTENCAO")

        self.assertEqual(OperationalStatus.EM_FUNCIONAMENTO, self.computer_case.operational_status)

    def test_rejects_status_change_during_assigned_computer_case_update(self):
        self.inventory_service.assign_computer_case_to_workstation(
            self.computer_case,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        with self.assertRaisesRegex(ValueError, "Assigned assets must have their status changed"):
            self.inventory_service.update_computer_case(
                self.computer_case,
                self._computer_case_data(
                    model="Updated model",
                    operational_status="EM_MANUTENCAO",
                ),
            )

        self.assertNotEqual("Updated model", self.computer_case.model)
        self.assertEqual(OperationalStatus.EM_FUNCIONAMENTO, self.computer_case.operational_status)

    def test_rejects_direct_status_change_for_assigned_monitor(self):
        self.inventory_service.assign_monitor_to_workstation(
            self.monitor,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        with self.assertRaisesRegex(ValueError, "Assigned assets must have their status changed"):
            self.inventory_service.set_monitor_status(self.monitor, "EM_MANUTENCAO")

        self.assertEqual(OperationalStatus.EM_FUNCIONAMENTO, self.monitor.operational_status)

    def test_rejects_status_change_during_assigned_monitor_update(self):
        self.inventory_service.assign_monitor_to_workstation(
            self.monitor,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        with self.assertRaisesRegex(ValueError, "Assigned assets must have their status changed"):
            self.inventory_service.update_monitor(
                self.monitor,
                self._monitor_data(
                    model="Updated monitor",
                    operational_status="DESATIVADO",
                ),
            )

        self.assertNotEqual("Updated monitor", self.monitor.model)
        self.assertEqual(OperationalStatus.EM_FUNCIONAMENTO, self.monitor.operational_status)

    def test_rejects_unassignment_without_reason(self):
        self.inventory_service.assign_monitor_to_workstation(
            self.monitor,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        with self.assertRaisesRegex(ValueError, "Movement reason is required."):
            self.inventory_service.unassign_monitor_from_workstation(
                self.workstation,
                self.technician,
                {"movement_reason": "", "operational_status": "FUNCIONAL_DESALOCADO"},
            )

    def test_rejects_invalid_unassignment_status(self):
        self.inventory_service.assign_monitor_to_workstation(
            self.monitor,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial installation"},
        )

        with self.assertRaisesRegex(ValueError, "Invalid unassignment status."):
            self.inventory_service.unassign_monitor_from_workstation(
                self.workstation,
                self.technician,
                {"movement_reason": "Invalid", "operational_status": "EM_FUNCIONAMENTO"},
            )

    def test_rejects_unassigned_asset_in_operation_status(self):
        with self.assertRaisesRegex(ValueError, "Unassigned assets cannot be in operation."):
            self.inventory_service.create_computer_case(
                self._computer_case_data(asset_tag="PAT-003", serial_number="SN-003", operational_status="EM_FUNCIONAMENTO")
            )

    def _computer_case_data(self, **overrides):
        data = {
            "asset_tag": "PAT-001",
            "serial_number": "SN-001",
            "manufacturer": "Dell",
            "model": "OptiPlex 3040",
            "operational_status": "FUNCIONAL_DESALOCADO",
        }
        data.update(overrides)
        return data

    def _monitor_data(self, **overrides):
        data = {
            "asset_tag": "MON-001",
            "serial_number": "MSN-001",
            "manufacturer": "Dell",
            "model": "E2216H",
            "screen_size_inches": "21.50",
            "display_connection": "HDMI",
            "operational_status": "FUNCIONAL_DESALOCADO",
        }
        data.update(overrides)
        return data


if __name__ == "__main__":
    unittest.main()
