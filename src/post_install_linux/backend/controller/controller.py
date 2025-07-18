import src.post_install_linux.backend.utils.utils as utils
from post_install_linux.backend.services.setups import Setup
from post_install_linux.backend.services.install_packages import Install_packages
from post_install_linux.backend.services.theme import Theme   
from post_install_linux.backend.env import get_password

class Controller():

    def __init__(self):
        utils.check_connection()
        password = get_password()
        self.self.setups = Setup(password=password)
        self.inp = Install_packages(password=password)
        self.self.theme = Theme(password=password)


    def setup_yay(self):
        self.setups.setup_yay()


    def test(self):
        self.configs_keyboard()

    def install_wallpapers(self):
        self.install_wallpapers()


    def install_dependencies(self):
        self.inp.install_dependencies()


    def install_packages(self):
        self.inp.install_packages()


    def install_fonts(self):
        self.inp.install_fonts()


    def install_debs(self):
        self.inp.downloads_debs()
        self.inp.install_debs()


    def install_flatpaks(self):
        self.inp.install_flatpaks()


    def install_snaps(self):
        self.inp.snaps_install()


    def install_intellij(self):
        self.inp.intellij_install()


    def install_rpms(self):
        self.inp.install_rpms()


    def install_gtk_theme(self):
        self.theme.gtk_theme()


    def setup_aliases_and_tools(self):
        self.setups.setup_aliases_and_tools()    


    def git_config(self):
        self.setups.git_config()


    def setup_tlp(self):
        self.setups.setup_tlp() 


    def setup_bt_service(self):
        self.setups.setup_bt_service()


    def configs(self): 
        self.setups.configs()


    def set_profile_picture_current_user(self):
        self.setups.set_profile_picture_current_user()   


    def set_configs_fastfetch(self):
        self.setups.set_configs_fastfetch() 


    def install_oh_my_bash(self):
        self.setups.install_oh_my_bash()


    def install_theme_grub(self):
        self.setups.install_theme_grub() 

    
    def install_minimal(self):
        self.setup_yay()
        self.install_dependencies()
        self.install_packages()
        self.install_flatpaks()
        self.install_snaps()
        self.configs()
        self.setup_aliases_and_tools()
        utils.ask_to_restart()

    
    def install_complete(self):
        self.setup_yay()
        self.install_dependencies()
        self.install_packages()
        self.install_fonts()
        self.install_debs()
        self.install_intellij()
        self.install_flatpaks()
        self.install_snaps()

        self.setup_aliases_and_tools()
        self.git_config()
        self.setup_tlp()
        self.setup_bt_service()
        self.configs()
        self.set_profile_picture_current_user()
        self.install_fonts()
        self.set_configs_fastfetch()
    
        utils.ask_to_restart()


    def install_full(self):
        self.setup_yay()
        self.install_dependencies()
        self.install_packages()
        self.install_fonts()
        self.install_debs()
        self.install_flatpaks()
        self.install_snaps()

        self.install_gtk_theme()

        self.setup_aliases_and_tools()
        self.install_theme_grub()
        self.git_config()
        self.setup_tlp()
        self.setup_bt_service()
        self.configs()
        self.set_profile_picture_current_user()
        self.install_fonts()
        self.set_configs_fastfetch()
        self.install_oh_my_bash()

        utils.ask_to_restart()
