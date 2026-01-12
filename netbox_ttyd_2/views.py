import socket
import subprocess
import os
import time
from django.shortcuts import render
from django.views.generic import View
from dcim.models import Device
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.conf import settings

class DeviceTtyd2View(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_device'

    def get_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def get(self, request, pk):
        device = Device.objects.get(pk=pk)
        return render(request, 'netbox_ttyd_2/terminal.html', {
            'device': device,
            'error': "Please use the Terminal button on the device page to login."
        })

    def post(self, request, pk):
        device = Device.objects.get(pk=pk)
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        ip_obj = device.primary_ip4 or device.primary_ip6
        if not ip_obj:
            return render(request, 'netbox_ttyd_2/terminal.html', {
                'device': device,
                'error': "Device has no management IP."
            })
        
        ip = str(ip_obj.address.ip)
        port = self.get_free_port()
        
        plugin_config = settings.PLUGINS_CONFIG.get('netbox_ttyd_2', {})
        ttyd_path = plugin_config.get('ttyd_path', 'ttyd')
        sshpass_path = plugin_config.get('sshpass_path', 'sshpass')

        # Prepare environment with SSHPASS
        env = os.environ.copy()
        env['SSHPASS'] = password

        # Construct command as a list
        # We use 'sshpass -e' to read password from environment variable SSHPASS
        full_cmd = [
            ttyd_path if os.name != 'nt' else f"{ttyd_path}.exe",
            "-p", str(port),
            "-i", "0.0.0.0",
            "--idle-timeout", "200",
            "--once",
            sshpass_path,
            "-e",  # Read password from SSHPASS env var
            "ssh",
            "-t",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=10",
            "-o", "PreferredAuthentications=password",
            f"{username}@{ip}"
        ]
            
        try:
            # Log the command for debugging (password is hidden in env)
            print(f"DEBUG: Starting ttyd on port {port} for {username}@{ip}")
            
            # Start ttyd process
            subprocess.Popen(full_cmd, env=env)
            
            # Give ttyd a moment to start
            time.sleep(1)
            
            # Use the same host as NetBox but different port
            host = request.get_host().split(':')[0]
            ttyd_url = f"http://{host}:{port}"
            
            return render(request, 'netbox_ttyd_2/terminal.html', {
                'device': device,
                'ttyd_url': ttyd_url,
            })
        except Exception as e:
            return render(request, 'netbox_ttyd_2/terminal.html', {
                'device': device,
                'error': f"Failed to start ttyd: {str(e)}"
            })
