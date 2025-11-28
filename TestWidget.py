import io
from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

from test_tiler import TileApp

# Scale
SCALE_MINIMUM = 2
SCALE_MAXIMUM = 14

class MyWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)

        self.scatter = Scatter(scale_min=SCALE_MINIMUM, scale_max=SCALE_MAXIMUM)
        
        tiler_obj = TileApp()
        
        
        
        # Bytest to texture tooling
        
        size1, size2, raw_image_bytes = tiler_obj.get_image_square_bytes_on_zoom(10)
        map_texture = Texture.create(size=(size1,size2))
        print(f"Size 1 {size1} Size 2 {size2}")
        map_texture.blit_buffer(raw_image_bytes,colorfmt='rgba', bufferfmt='ubyte')
        
        
        
        # image = Image(source='i-can-has-cheezburger-cat.jpg')
    
        self.scatter.size = map_texture.size
        
        self.scatter.add_widget(Image(texture=map_texture, size=map_texture.size, size_hint=(None,None)))
        
        

        self.scatter.pos = (300, 300)
        self.scatter.scale = 1

        # Bind all properties to a single handler function
        self.scatter.bind(
            pos=self.on_transform_change,
            scale=self.on_transform_change,
            rotation=self.on_transform_change
        )

        self.add_widget(self.scatter)
        
        ''' ********** DATABASE COMMS TOOLING ********** '''
        
        
        
        #self.get_tile(1,1,1)
        
        
        
        
        ''' ********** IMAGE TILING TOOLING ********** '''
        
        self.visible_tiles = []
        

    def on_transform_change(self, instance, value):
        # Now you can always get the current scale (and pos/rotation)
        print(f"Scatter transformed: Pos={instance.pos}, Scale={instance.scale}, Rotation={instance.rotation}")
        # You can use instance.scale here for other logic
    
    
    
    ''' 
        CREATE TABLE tiles (zoom_level integer, tile_column integer, tile_row integer, tile_data blob);
        CREATE UNIQUE INDEX tile_index on tiles (zoom_level, tile_column, tile_row);
    '''
        
    def get_metadata(self):
        self.database_cursor.execute('select * from metadata')
        return self.database_cursor.fetchall()
    
    def get_tile(self,zoom, column, row):
        self.database_cursor.execute('SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?', (zoom,column,row))
        raw_tile_binary = self.database_cursor.fetchone()
        image_stream = io.BytesIO(raw_tile_binary)
        core_image = CoreImage(image_stream, ext='png') # or 'jpeg', 'bmp', etc.
        
        
        self.scatter.add_widget(core_image)
        
        
        

        