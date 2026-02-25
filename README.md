pyinstaller --name "Autologin" --splash "assets/splash_logo.jpg" --onefile --noconsole --add-data "assets\\*;assets" --add-data "screens/json/portal_map.json;json" --add-data ".env;." --add-data "json\\*;json" --add-data "assets\\logo.jpg;assets" main.py --hidden-import=pyi_splash

bangautologin
pyinstaller --name "bangautologin" --splash "assets/splash_logo.jpg" --onefile --noconsole --add-data "assets\;assets" --add-data "screens/json/portal_map.json;json" --add-data ".env;." --add-data "assets\logo.jpg;assets" bangautologin.py --hidden-import=pyi_splash

