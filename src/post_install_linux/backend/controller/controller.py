import src.post_install_linux.backend.utils.utils as utils
import post_install_linux.backend.services.setups as setups
import post_install_linux.backend.services.install_packages as inp
import post_install_linux.backend.utils.theme as theme    
from post_install_linux.backend.env import TEMP_DIR, DISTRO, DATA_DIR, JSON_DIR, ZIP_DIR

class Controller():

    def __init__(self):
        utils.check_connection()


    def setup_yay(self):
        setups.setup_yay()


    def test(self):
        setups.configs_keyboard()

    def install_wallpapers(self):
        theme.install_wallpapers()


    def install_dependencies(self):
        inp.install_dependencies()


    def install_packages(self):
        inp.install_packages()


    def install_fonts(self):
        inp.install_fonts()


    def install_debs(self):
        inp.downloads_debs()
        inp.install_debs()


    def install_flatpaks(self):
        inp.install_flatpaks()


    def install_snaps(self):
        inp.snaps_install()


    def install_intellij(self):
        inp.intellij_install()


    def install_rpms(self):
        inp.install_rpms()


    def install_gtk_theme(self):
        theme.gtk_theme()


    def setup_aliases_and_tools(self):
        setups.setup_aliases_and_tools()    


    def git_config(self):
        setups.git_config()


    def setup_tlp(self):
        setups.setup_tlp() 


    def setup_bt_service(self):
        setups.setup_bt_service()


    def configs(self): 
        setups.configs()


    def set_profile_picture_current_user(self):
        setups.set_profile_picture_current_user()   


    def configs_keyboard(self):
        setups.configs_keyboard()  


    def set_configs_fastfetch(self):
        setups.set_configs_fastfetch() 


    def install_oh_my_bash(self):
        setups.install_oh_my_bash()


    def install_theme_grub(self):
        setups.install_theme_grub() 

    
    def install_minimal(self):
        self.setup_yay()
        self.install_dependencies()
        self.install_packages()
        self.install_flatpaks()
        self.install_snaps()
        self.configs_keyboard()
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
        self.configs_keyboard()
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
        self.configs_keyboard()
        self.install_fonts()
        self.set_configs_fastfetch()
        self.install_oh_my_bash()

        utils.ask_to_restart()

    def get_apps(self):
        return utils.get_data(DISTRO, "apps")