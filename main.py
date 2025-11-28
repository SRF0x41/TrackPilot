# Base kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework
from kivy.uix.slider import Slider

# Map imports
from kivy_garden.mapview import MapView, MapMarker
from kivy_garden.mapview.mbtsource import MBTilesMapSource

import json
import requests
import os
# from dotenv import load_dotenv

# Custom classes
from Navigation import Navigation
from DataStore import DataStore
from datetime import datetime
# from DataBrocker import DataBrocker  # Cryptography build isn't working
from DataLink import DataLink

from pathlib import Path
import sqlite3

# Custom widgets
from TestWidget import MyWidget


# Overwrites the class to create a local cache file
class IOSMBTilesSource(MBTilesMapSource):
    def __init__(self, **kwargs):
        base = Path(os.getenv("HOME")) / "Library" / "Caches" / "mapview"
        base.mkdir(parents=True, exist_ok=True)
        kwargs["cache_dir"] = str(base)
        super().__init__(**kwargs)


class LRT(App):
    def build(self):
        # print(f"My env var {os.getenv("TEST_ENV")}")

        """ ********** ALLOW APP TO RUN GPS UPDATES IN THE BACKGROUND *********** """
        load_framework('/System/Library/Frameworks/CoreLocation.framework')

        # Grab Objective-C classes
        CLLocationManager = autoclass('CLLocationManager')
        CLLocationManagerDelegate = autoclass('NSObject')

        self.enable_background_location()

        """ ---------- UI SET UP ---------- """
        layout = BoxLayout(
            orientation='vertical',
            padding=[10, 120, 10, 150],  # [left, top, right, bottom]
            spacing=10
        )
        
        
        ''' ********** TEST WIDGET ********** '''
        test_widget = MyWidget()
        layout.add_widget(test_widget)
        
        

        """ ---------- MAP ---------- """
        self.APP_PATH = self.user_data_dir
        """
        for root, dirs, files in os.walk(self.APP_PATH):
            for f in files:
                if f.endswith(".mbtiles"):
                    print(f"  File: {os.path.join(root, f)}")

        print(f"TEST PATH {self.APP_PATH}/satellite-2017-11-02_us_colorado.mbtiles")

        mbtiles_path = os.path.abspath("satellite-2017-11-02_us_colorado.mbtiles")
        print(f"TEST OS ABS PATH {mbtiles_path}")

        mbtiles_source = IOSMBTilesSource(
            filename=mbtiles_path,
            min_zoom=5,
            max_zoom=12,
            attribution="",
            tile_size=256
        )

        # Colorado bounding box
        mbtiles_source.bounds = (-109.0631, 36.98943, -102.041, 41.00372)

        # Prevent fallback to online tiles
        mbtiles_source.no_map = True

        # Create the mapview with this source
        mapview = MapView(
            zoom=5,
            lat=38.996575,
            lon=-105.55205000000001,
            map_source=mbtiles_source,
            pause_on_action=False,
        )

        # layout.add_widget(mapview)"""
        
        ''' ********** MONITER WIDGET ********** '''
        self.moniter_text_buffer = []
        self.system_moniter = Label(
            text="Press start gps data collection",
            font_name="RobotoMono-Regular",
            halign="left",
            valign="top",
            text_size=(1000, None),
            size_hint=(1, 1)
        )
        # layout.add_widget(self.system_moniter)

        ''' ********** TOGGLE GPS SYSTEM WIDGET ********** '''
        self.toggle_record_data = False
        toggle_gps_system = Button(
            text="Toggle GPS",
            size_hint=(1, 0.4)
        )
        toggle_gps_system.bind(on_press=self.toggle_start_gps_system)
        # layout.add_widget(toggle_gps_system)

        delete_local_data_button = Button(
            text='Delete Local Data',
            size_hint=(1, 0.4)
        )
        delete_local_data_button.bind(on_press=self.delete_local_data)
        # layout.add_widget(delete_local_data_button)

        """ ********** GLOBAL POSITIONING SYSTEM RECORD START ********** """
        self.data_store_obj = DataStore(self.APP_PATH)
        self.nav_object = Navigation(self.nav_object_callback)
        # self.data_store_obj.see_full_path_data()

        """ ********** CLIENT SIDE DATA LINK ********** """
        push_local_data_to_server_button = Button(
            text='Push data to server',
            size_hint=(1, 0.4)
        )
        push_local_data_to_server_button.bind(on_press=self.push_local_data_to_server)
        # layout.add_widget(push_local_data_to_server_button)

        return layout

    def on_slider_value_change(self, instance, value):
        self.value_label.text = f"Slider Value: {int(value)}"

    """ Apple pyobjus magic function """
    def enable_background_location(self):
        CLLocationManager = autoclass('CLLocationManager')
        self.location_manager = CLLocationManager.alloc().init()

        self.location_manager.allowsBackgroundLocationUpdates = True
        self.location_manager.pausesLocationUpdatesAutomatically = False

        self.location_manager.requestAlwaysAuthorization()
        self.location_manager.startUpdatingLocation()

        print("Background GPS tracking enabled.")

    def nav_object_callback(self, **kwargs):
        self.data_store_obj.record_gps_data(**kwargs)
        number_of_current_day_entries = self.data_store_obj.get_current_day_entries_count()
        self.append_text_line_moniter(f"Number of Entries: {number_of_current_day_entries}")

    def append_text_line_moniter(self, text):
        if len(self.moniter_text_buffer) > 15:
            self.moniter_text_buffer.pop(0)
        self.moniter_text_buffer.append(text)
        setattr(self.system_moniter, 'text', '\n'.join(self.moniter_text_buffer))

    def append_text_moniter(self, text_list):
        text_list_length = len(text_list)
        lines_to_remove = 15 - text_list_length

        if lines_to_remove <= 0:
            self.moniter_text_buffer = text_list[-15:]
        else:
            for _ in range(lines_to_remove):
                self.moniter_text_buffer.pop(0)
            self.moniter_text_buffer.append(text_list)

    def toggle_start_gps_system(self, instance):
        self.toggle_record_data = not self.toggle_record_data
        state_text = 'GPS Data Collection On' if self.toggle_record_data else 'GPS Data Collection Off'
        print(f"GPS system toggled {state_text}")
        instance.text = state_text

        if self.toggle_record_data:
            self.nav_object.start()
        else:
            self.nav_object.stop()

    def delete_local_data(self, instance):
        self.data_store_obj.DELETE_EVERYTHING(self.APP_PATH)
        self.append_text_line_moniter("Local data deleted")

    """ ********** SERVER UTILITIES ********** """
    def push_local_data_to_server(self, instance):
        data_link_obj = DataLink()

        all_local_files_canon_paths = self.data_store_obj.get_all_file_canon_paths()
        print("ALL LOCAL FILES")
        print(all_local_files_canon_paths)

        data_link_obj.establish_connection_server()
        for i in range(3):
            data_link_obj.file_data_stream(all_local_files_canon_paths[i])

        data_link_obj.close_socket()


if __name__ == '__main__':
    app = LRT()
    app.run()
