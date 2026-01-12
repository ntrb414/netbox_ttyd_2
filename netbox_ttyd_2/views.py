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

        # Construct command
        # -p: port
        # -i 200: idle timeout in seconds (200s)
        # --once: exit after one session
        if os.name == 'nt': # Windows
            cmd = f'{ttyd_path}.exe -p {port} -i 200 --once {sshpass_path} -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{ip}'
        else: # Linux
            cmd = f'{ttyd_path} -p {port} -i 200 --once {sshpass_path} -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{ip}'
            
        try:
            # Start ttyd process
            subprocess.Popen(cmd, shell=True)
            
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
