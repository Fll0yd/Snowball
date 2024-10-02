import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import threading
import time

# Add the parent directory to the sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from core.system_monitor import SystemMonitor, FanMonitor, VisualMonitor, run_windows_defender_scan, check_disk_health, run_sfc_scan

class TestSystemMonitor(unittest.TestCase):

    @patch('core.logger.SnowballLogger.log_system_health')
    @patch('core.logger.SnowballLogger.notify_user')
    @patch('core.logger.SnowballLogger.log_warning')
    @patch('core.logger.SnowballLogger.log_error')
    def setUp(self, mock_log_error, mock_log_warning, mock_notify_user, mock_log_system_health):
        """Set up the SystemMonitor instance before each test."""
        self.monitor = SystemMonitor(cpu_threshold=50, memory_threshold=50, temp_threshold=75)
        self.mock_log_system_health = mock_log_system_health
        self.mock_notify_user = mock_notify_user
        self.mock_log_warning = mock_log_warning
        self.mock_log_error = mock_log_error

    @patch('psutil.cpu_percent')
    def test_check_cpu_usage(self, mock_cpu_percent):
        """Test CPU usage checking."""
        mock_cpu_percent.return_value = 60  # Simulate high CPU usage
        cpu_usage = self.monitor.check_cpu_usage()
        self.assertEqual(cpu_usage, 60)
        self.mock_notify_user.assert_called_with("High CPU Usage", "CPU usage is at 60%")

    @patch('psutil.virtual_memory')
    def test_check_memory_usage(self, mock_virtual_memory):
        """Test memory usage checking."""
        mock_virtual_memory.return_value.percent = 70
        memory_usage = self.monitor.check_memory_usage()
        self.assertEqual(memory_usage, 70)
        self.mock_notify_user.assert_called_with("High Memory Usage", "Memory usage is at 70%")

    @patch('core.system_monitor.FanMonitor')
    def test_fan_monitor(self, mock_fan_monitor):
        """Test fan speed monitoring."""
        mock_fan = mock_fan_monitor.return_value  # Get the mocked FanMonitor instance
        mock_fan.print_fan_speeds.return_value = [("Fan1", 1200)]  # Set the return value

        # Call the method to get fan speeds
        fan_speeds = self.monitor.check_fan_speeds()
        
        self.assertEqual(fan_speeds, [("Fan1", 1200)])  # Assert the expected output

    @patch('os.system')
    def test_run_windows_defender_scan(self, mock_system):
        """Test running Windows Defender quick scan."""
        run_windows_defender_scan()
        mock_system.assert_called_once_with('powershell Start-MpScan -ScanType QuickScan')

    @patch('os.system')
    def test_check_disk_health(self, mock_system):
        """Test running disk health check (chkdsk)."""
        check_disk_health()
        mock_system.assert_called_once_with('schtasks /create /tn "CheckDisk" /tr "chkdsk /f /r" /sc onstart')

    @patch('os.system')
    def test_run_sfc_scan(self, mock_system):
        """Test running SFC scan for file system health."""
        run_sfc_scan()
        mock_system.assert_called_once_with('sfc /scannow')

    @patch('core.system_monitor.GPUtil.getGPUs')
    def test_check_gpu_usage(self, mock_getGPUs):
        mock_gpu = MagicMock()
        mock_gpu.name = 'NVIDIA GeForce RTX 2060'
        mock_gpu.load = 0.70  # 70% GPU usage
        mock_gpu.temperature = 65  # 65°C
        mock_getGPUs.return_value = [mock_gpu]

        gpu_usage, gpu_temp = self.monitor.check_gpu_usage()
        self.assertEqual(gpu_usage, 70)
        self.assertEqual(gpu_temp, 65)
        self.mock_notify_user.assert_called_with(
            "High GPU Usage or Temperature", 
            f"GPU {mock_gpu.name}: {gpu_usage:.1f}% load, {gpu_temp}°C"
        )

    @patch('pystray.Icon')
    def test_system_tray_icon(self, mock_icon):
        """Test the system tray icon for interaction."""
        mock_icon_instance = mock_icon.return_value
        tray_thread = threading.Thread(target=self.monitor.start_system_tray_with_duck_icon)
        tray_thread.start()
        
        time.sleep(1)
        
        mock_icon_instance.run.assert_called_once()

    def test_memory_leak_detection(self):
        """Test memory leak detection."""
        with patch('psutil.process_iter') as mock_process_iter:
            mock_process_iter.return_value = [
                MagicMock(info={'pid': 1, 'name': 'Process1', 'memory_percent': 15}),
                MagicMock(info={'pid': 2, 'name': 'Process2', 'memory_percent': 8})
            ]
            self.monitor.detect_memory_leak()  # Should not raise errors
            mock_process_iter.assert_called_once()

    def test_network_spikes(self):
        """Test detection of network traffic spikes."""
        with patch('psutil.net_io_counters') as mock_net_io:
            mock_net_io.return_value.bytes_sent = 0
            mock_net_io.return_value.bytes_recv = 0
            self.monitor.monitor_network_spikes()  # Should not raise errors

    @patch('psutil.sensors_temperatures')
    def test_temperature_monitoring(self, mock_sensors_temperatures):
        """Test temperature monitoring."""
        mock_sensors_temperatures.return_value = {
            'coretemp': [MagicMock(current=85)]
        }
        temperature = self.monitor.check_temperature()
        self.assertEqual(temperature, 85)
        self.mock_notify_user.assert_called_with("High coretemp Temperature", "coretemp temperature: 85°C")

    @patch('psutil.disk_partitions')
    @patch('psutil.disk_usage')
    def test_disk_usage_monitoring(self, mock_disk_usage, mock_disk_partitions):
        """Test disk usage monitoring."""
        mock_disk_partitions.return_value = [
            MagicMock(device='C:', mountpoint='/')
        ]
        mock_disk_usage.return_value.percent = 90  # Simulate high disk usage
        disk_data = self.monitor.check_disk_usage()
        self.assertEqual(disk_data, [('C:', 90)])
        self.mock_log_error.assert_not_called()  # Ensure no error logs were triggered

    @patch('psutil.disk_partitions')
    @patch('psutil.disk_usage')
    def test_check_disk_usage(self, mock_disk_partitions, mock_disk_usage):
        mock_disk_partitions.return_value = [MagicMock(device='C:', mountpoint='/'), MagicMock(device='D:', mountpoint='/')]
        mock_disk_usage.side_effect = [MagicMock(percent=50), OSError("Drive not ready")]

        disk_data = self.monitor.check_disk_usage()
        self.assertEqual(disk_data, [('C:', 50)])  # Only the C: drive should be accessible
    
    @patch('psutil.net_io_counters')
    def test_monitor_network_spikes(self, mock_net_io_counters):
        mock_net_io_counters.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)
        self.monitor.monitor_network_spikes()
        # Add assertions to validate behavior

    def test_thread_safety_system_monitoring(self):
        """Test thread safety for system monitoring."""
        def run_monitor_in_thread(monitor):
            monitor.monitor_system()

        threads = [threading.Thread(target=run_monitor_in_thread, args=(self.monitor,)) for _ in range(5)]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.mock_log_system_health.assert_called()  # Ensure logging was performed

    def test_backup_status_check(self):
        """Test backup status monitoring."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False  # Simulate missing backup file
            self.monitor.check_backup_status()
            self.mock_notify_user.assert_called_with("Backup Issue", "Backup file not found. Please check your backup routine.")

    def test_visual_monitor(self):
        """Test the visual monitor functionality."""
        visual_monitor = VisualMonitor()  # Ensure it initializes without errors

    @patch('psutil.process_iter')
    def test_check_running_processes(self, mock_process_iter):
        mock_process_iter.return_value = [
            MagicMock(info={'pid': 0, 'name': 'System Idle Process', 'cpu_percent': 1.0}),
            MagicMock(info={'pid': 42776, 'name': 'python.exe', 'cpu_percent': 20.0}),
        ]
        processes = self.monitor.check_running_processes()
        self.assertEqual(processes[0][2], 1.0)  # Ensure idle process CPU usage is low

if __name__ == "__main__":
    unittest.main()
