try:
    from netbox.plugins import PluginConfig
except ImportError:
    from extras.plugins import PluginConfig

class Ttyd2Config(PluginConfig):
    name = 'netbox_ttyd_2'
    verbose_name = 'Ttyd Web Terminal 2'
    description = 'Integrate ttyd for device web SSH (v2)'
    version = '0.1'
    base_url = 'ttyd-2'
    default_settings = {
        'ttyd_path': 'ttyd',  # Path to ttyd executable
        'sshpass_path': 'sshpass', # Path to sshpass executable
    }

config = Ttyd2Config
